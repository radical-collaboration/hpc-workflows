from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

_KERNEL_INFO = {
    "name":         "compute_analog_for_one_station",                  # Mandatory
    "description":  "sleeping kernel",        # Optional
    "arguments":   {},
    "machine_configs":                        # Use a dictionary with keys as
        {                                     # resource names and values specific
            "local.localhost":                # to the resource
            {
                "environment" : None,         # dict or None, can be used to set env variables
                "pre_exec"    : None,         # list or None, can be used to load modules
                "executable"  : ["/bin/sleep"],        # specify the executable to be used
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
        arguments  = ["-L -l -d /Users/wuh20/data/data_windLuca -o results_for_station_1.txt --stations 1"]

        self._executable  = '/Users/wuh20/Desktop/canalogsmp'
        self._arguments   = arguments
        self._environment = None 
        self._uses_mpi    = None
        self._pre_exec    = None
