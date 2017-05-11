from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

_KERNEL_INFO = {
    "name":         "compute_analog_for_one_station",                  # Mandatory
    "description":  "sleeping kernel",        # Optional
    "arguments":   {
                '--data=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Location of the data"
                            },
                '--output=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Location of output"
                            },

                '--stations=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Number of stations"
                            },


    },
    "machine_configs":                        # Use a dictionary with keys as
        {                                     # resource names and values specific
            "local.localhost":                # to the resource
            {
                "environment" : None,         # dict or None, can be used to set env variables
                "pre_exec"    : ['export PATH=$PATH:/Users/wuh20/Desktop'], # list or None, can be used to load modules
                "executable"  : 'canalogsmp',        # specify the executable to be used
                "uses_mpi"    : False         # mpi-enabled? True or False
            },

            "xsede.stampede":                # to the resource
            {
                "environment" : None,         # dict or None, can be used to set env variables
                "pre_exec"    : [   'module load gcc',
                                            'module load boost',
                                            'export PATH=$PATH:/work/02734/vivek91/modules/analog_ensemble/src'], # list or None, can be used to load modules
                "executable"  : 'canalogsmp',        # specify the executable to be used
                "uses_mpi"    : False         # mpi-enabled? True or False
            },

            "xsede.comet":                # to the resource
            {
                "environment" : None,         # dict or None, can be used to set env variables
                "pre_exec"    : ['export PATH=$PATH:/home/vivek91/modules/hpc-workflows/scripts/application_AnEn/src'], # list or None, can be used to load modules
                "executable"  : 'canalogsmp',        # specify the executable to be used
                "uses_mpi"    : False         # mpi-enabled? True or False
            },

        }
}

# ------------------------------------------------------------------------------
#
class compute_analog_kernel(KernelBase):

    def __init__(self):

        super(compute_analog_kernel, self).__init__(_KERNEL_INFO)
        """Le constructor."""

    # --------------------------------------------------------------------------
    #
    @staticmethod
    def get_name():
        return _KERNEL_INFO["name"]


    def _bind_to_resource(self, resource_key):
        """This function binds the Kernel to a specific resource defined in
        "resource_key".
        """

        cfg = _KERNEL_INFO["machine_configs"][resource_key]

        arguments  = ['-L','-l',
                      '-d', self.get_arg('--data='),
                      '-o', self.get_arg('--output='),
                      '--stations',self.get_arg('--stations=')
                    ]

        self._executable  = cfg['executable']
        self._arguments   = arguments
        self._environment = None
        self._uses_mpi    = None
        self._pre_exec    = cfg['pre_exec']
