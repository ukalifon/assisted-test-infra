#!/bin/bash

source scripts/utils.sh

export PROFILE=${PROFILE:-assisted-installer}

function configure_minikube() {
    echo "Configuring minikube..."
    minikube config set ShowBootstrapperDeprecationNotification false
    minikube config set WantUpdateNotification false
    minikube config set WantReportErrorPrompt false
    minikube config set WantKubectlDownloadMsg false
}

function init_minikube() {
    #If the vm exists, it has already been initialized
    for p in $(virsh -c qemu:///system list --name ); do
        if [[ $p == $PROFILE ]]; then
            return
        fi
    done

    minikube start --driver=kvm2 --memory=8192 --cpus=4 --profile=${PROFILE} --force --wait-timeout=15m0s --disk-size=50g
    minikube tunnel --cleanup &> /dev/null &
}

if [ "${DEPLOY_TARGET}" != "minikube" ]; then
    exit 0
fi

configure_minikube
as_singleton init_minikube