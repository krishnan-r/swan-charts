#!/bin/bash
# set swan k8s env.

PS3='Choose SWAN k8s environment: '

select opt in 'SWAN Prod' 'SWAN QA' 'Spark K8s' 'Quit'
do
    case $opt in
        "SWAN Prod")
            export KUBECONFIG_DATA=$(tbag show --hg swan swan_prod_k8s_kubeconfig | jq -r '.secret' | base64 -w0)
            ;;
        "SWAN QA")
            export KUBECONFIG_DATA=$(tbag show --hg swan swan_qa_k8s_kubeconfig | jq -r '.secret' | base64 -w0)
            ;;
        "Spark K8s")
            export KUBECONFIG_DATA=$(tbag show --hg swan spark_k8s_kubeconfig | jq -r '.secret' | base64 -w0)
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
    alias kubectl="kubectl --kubeconfig <(echo $KUBECONFIG_DATA | base64 --decode)"

    if [ "${ZSH_VERSION-}" ]; then
        source <(kubectl completion zsh)
        export PS1="%F{red}[\$opt]%f [%n@%m ]%$ "
    else
        source <(kubectl completion bash)
        export PS1="\e[0;31m\$opt\e[m [\u@\h \W]\$ "
    fi

    echo 'alias k=kubectl' >>~/.bashrc
    complete -F __start_kubectl k

    break
done
