# WARNING: nodes ids/names in managed_elements cannot be substrings of each other
# example: managed_elements = ["5G132PCC001" "E5G132PCC001"] is NOT SUPPORTED
managed_elements = ["5G132PCC001", "5G132PCC002"]
pmics = ["pmic1", "pmic2"]


# WARNING: nodes_names in managed_elements_objects cannot be substrings of each other
# managed_elements_objects is similar to managed_elements
# this var is used to add/delete nodes to/from ENM
managed_elements_objects = [
    {
        "node_name": "5G132PCC001",
        "node_type":"PCC",
        "ossModelIdentity":"1.9",
        "ip_address":"30.0.11.161"
    },
    {
        "node_name": "5G132PCC002",
        "node_type":"PCC",
        "ossModelIdentity":"1.9",
        "ip_address":"30.0.11.168"
    } ]