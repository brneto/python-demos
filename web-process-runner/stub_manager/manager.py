import os
import subprocess
from threading import Thread
import logging


class StubManager:
    __process = None

    def __init__(self, port=8080, consumer=None):
        self.__port = port
        self.start(consumer)

    def start(self, consumer=None):
        self.__validate_consumer(consumer)
        if type(self).__process is not None:
            self.terminate()
        command = self.__build_command()
        self.__run_process(command)
        return type(self).__process

    def __validate_consumer(self, consumer):
        if consumer is None:
            raise AttributeError("consumer name parameter has not been defined")
        self.__consumer = consumer

    def terminate(self):
        process = type(self).__process
        process.terminate()
        try:
            process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()

    def __build_command(self):
        repository = os.environ['M2_REPO']
        group_id = os.environ['GROUP_ID'].replace("/", ".")[1:]
        artifact_id = os.environ['ARTIFACT_ID']
        version = os.environ['DEP_VERSION']

        port = self.__port
        command = ["java", "-Djava.security.egd=file:/dev/./urandom",
                   "-jar", "./stub-runner.jar", f"--server.port={port - 1}",
                   f"--stubrunner.ids={group_id}:{artifact_id}:{version}:{port + 1}",
                   "--stubrunner.stubsMode=LOCAL",
                   f"--stubrunner.repositoryRoot={repository}"]

        if 'JAVA_OPTS' in os.environ and os.environ['JAVA_OPTS'].strip():
            command = command[:2] + [os.environ['JAVA_OPTS']] + command[2:]

        consumer = self.__consumer
        if consumer is not None:
            command.extend([
              "--stubrunner.stubsPerConsumer=true",
              f"--stubrunner.consumerName={consumer}"])

        logging.info(f"CMD:{command}")
        return command

    def __run_process(self, command):
        type(self).__process = subprocess.Popen(command,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                universal_newlines=True,
                                                bufsize=0)
        Thread(name="stub-runner", target=self.__log_output).start()

    def __log_output(self):
        process = type(self).__process

        exit_code = process.poll()
        while exit_code is None:
            self.__print_log(process.stdout)
            exit_code = process.poll()

        logging.error(f"STUB:exit-code {exit_code}")
        self.__print_log(process.stderr)
        self.__print_log(process.stdout)

    def __print_log(self, output):
        if not output.closed:
            logging.info(f"STUB:{output.readline().strip()}")  # Blocking call
