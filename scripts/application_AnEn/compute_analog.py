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

                '--stations-ID=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Station ID"
                            },

                 '--cores=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Number of cores to be used"
                            },

                '--test_start=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Number of cores to be used"
                            },

                '--test_end=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Number of cores to be used"
                            },

                '--train_start=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Number of cores to be used"
                            },

                '--train_end=': {
                                "mandatory": True,                # Mandatory argument? True or False
                                "description": "Number of cores to be used"
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
                                            'export PATH=/home1/04672/tg839717/git/Analogs-portable/build:$PATH'], # list or None, can be used to load modules
                "executable"  : 'canalogs',        # specify the executable to be used
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
                      '--stations-ID',self.get_arg('--stations-ID='),
                      '--number-of-cores', self.get_arg('--cores='),
                      '--test-ID-start', self.get_arg('--test_start='),
                      '--test-ID-end', self.get_arg('--test_end='),
                      '--train-ID-start', self.get_arg('--train_start='),
                      '--train-ID-end', self.get_arg('--train_end=')
                    ]

        self._executable  = cfg['executable']
        self._arguments   = arguments
        self._environment = None
        self._uses_mpi    = None
        self._pre_exec    = cfg['pre_exec']
