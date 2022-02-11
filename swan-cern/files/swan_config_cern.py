import os, subprocess

from kubernetes import client
from kubernetes.client.rest import ApiException

"""
Class handling KubeSpawner.modify_pod_hook(spawner,pod) call
"""

class SwanPodHookHandlerProd(SwanPodHookHandler):

    def get_swan_user_pod(self):
        super().get_swan_user_pod()

        # ATTENTION Spark requires this side container, so we need to create it!!
        # Check if we should add the EOS path in the firstplace
        # if hasattr(self.spawner, 'local_home') and \
        #     not self.spawner.local_home:

        notebook_container = self._get_pod_container('notebook')


        # Set server hostname of the pod running jupyterhub
        notebook_container.env = self._add_or_replace_by_name(
            notebook_container.env,
            client.V1EnvVar(
                name='SERVER_HOSTNAME',
                value_from=client.V1EnvVarSource(
                    field_ref=client.V1ObjectFieldSelector(
                        field_path='spec.nodeName'
                    )
                )
            )
        )

        if self._gpu_enabled():
            # spc_t type is added as recommended by CM
            spc_t_selinux = client.V1SELinuxOptions(
                type = "spc_t"
            )
            security_context = client.V1PodSecurityContext(
                se_linux_options = spc_t_selinux
            )
            self.pod.spec.security_context = security_context

        return self.pod

# https://jupyterhub-kubespawner.readthedocs.io/en/latest/spawner.html
# This is defined in the configuration to allow overring iindependently 
# of which config file is loaded first
# c.SwanKubeSpawner.modify_pod_hook = swan_pod_hook
def swan_pod_hook_prod(spawner, pod):
    """
    :param spawner: Swan Kubernetes Spawner
    :type spawner: swanspawner.SwanKubeSpawner
    :param pod: default pod definition set by jupyterhub
    :type pod: client.V1Pod

    :returns: dynamically customized pod specification for user session
    :rtype: client.V1Pod
    """
    pod_hook_handler = SwanPodHookHandlerProd(spawner, pod)
    return pod_hook_handler.get_swan_user_pod()


swan_cull_period = get_config('custom.cull.every', 600)

c.SwanKubeSpawner.modify_pod_hook = swan_pod_hook_prod

# Required for swan systemuser.sh
c.SwanKubeSpawner.cmd = None