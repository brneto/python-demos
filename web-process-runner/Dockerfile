FROM opensuse/leap

EXPOSE 8080
EXPOSE 8081

ARG VERSION

ENV APP_DIR "/stubs-runner"

ENV JAVA_OPTS "-Djava.security.egd=file:/dev/urandom"

ENV M2_REPO "/root/.m2/repository"
ENV GROUP_ID "/ie/learn/python/demo"
ENV ARTIFACT_ID "stub-app"
ENV DEP_VERSION ${VERSION}

ENV NEXUS_REPO "https://localhost/nexus/content/repositories"
ENV RUNNER_REPO "https://repo1.maven.org/maven2/org/springframework/cloud/spring-cloud-contract-stub-runner-boot"
ENV RUNNER_VERSION "2.2.4.RELEASE"

RUN zypper --non-interactive install java-11-openjdk-headless \
&& zypper --non-interactive install shadow \
&& zypper clean --all

RUN zypper in -l -y glibc-locale curl wget python3 python3-pip \
&& zypper clean -a \
&& rm -rf /var/cache/zypp

RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
RUN pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org pipenv

RUN mkdir -p ${APP_DIR}
RUN wget --no-check-certificate -O ${APP_DIR}/stub-runner.jar \
"${RUNNER_REPO}/${RUNNER_VERSION}/spring-cloud-contract-stub-runner-boot-${RUNNER_VERSION}.jar"

RUN mkdir -p ${M2_REPO}${GROUP_ID}/${ARTIFACT_ID}/${DEP_VERSION}

RUN wget --no-check-certificate -O \
${M2_REPO}${GROUP_ID}/${ARTIFACT_ID}/maven-metadata.xml \
"${NEXUS_REPO}${GROUP_ID}/${ARTIFACT_ID}/maven-metadata.xml"

RUN wget --no-check-certificate -O \
${M2_REPO}${GROUP_ID}/${ARTIFACT_ID}/${DEP_VERSION}/${ARTIFACT_ID}-${DEP_VERSION}-stubs.jar \
"${NEXUS_REPO}${GROUP_ID}/${ARTIFACT_ID}/${DEP_VERSION}/${ARTIFACT_ID}-${DEP_VERSION}-stubs.jar"

COPY Pipfile Pipfile.lock entrypoint.py ${APP_DIR}/
COPY stub_manager ${APP_DIR}/stub_manager
WORKDIR ${APP_DIR}

ENV LC_ALL "C.UTF-8"
ENV LANG "C.UTF-8"
RUN python3 -m pipenv install --deploy --system

# https://github.com/moby/moby/issues/12447#issuecomment-94417192
ENTRYPOINT ["/usr/bin/python3", "-u", "./entrypoint.py", "8080"]
CMD ["pristine"]
