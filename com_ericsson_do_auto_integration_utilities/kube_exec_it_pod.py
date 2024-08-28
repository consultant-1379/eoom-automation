def get_exec_pod_it_command(namespace, pod, command):
    cmd = f"kubectl -n {namespace} exec -it {pod} -- {command}"
    return cmd

def get_exec_pod_it_command_sql(namespace, pod, container_name,  user, db_name ,sql):
    cmd = f"kubectl -n {namespace} exec -it {pod} -c {container_name} -- psql -U {user} -d {db_name} -Atqc \"{sql}\""
    return cmd
