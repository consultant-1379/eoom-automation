# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************
import time

from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from packaging import version

log = Logger.get_logger('VM_VNFM_OPERATIONS.py')


def get_VMVNFM_host_connection(ccd1=False):
    """
    This method will give the connection
    of eccd server , where vm-vnfm is hosted
    """
    try:
        log.info('Start connecting with VM-VNFM host server ')

        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        log.info('ecm ip : %s, ecm username : %s, ecm password : %s', ecm_server_ip, ecm_username, ecm_password)

        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        global vm_vnfm_namespace

        vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
        log.info('Using namespace: %s', vm_vnfm_namespace)

        if vm_vnfm_namespace == 'codeploy' and (ccd1 is False):
            file_path = 'id_rsa_tf.pem'
            log.info('Using key: %s', file_path)

        elif vm_vnfm_namespace == 'eo-deploy':
            file_path = 'eccd-2-3.pem'
            log.info("Using key: %s", file_path)

        else:
            file_path = 'eccd-2-3.pem'
            log.info('Using key: %s', file_path)

        (
            vm_vnfm_director_ip,
            vm_vnfm_director_username,
        ) = Server_details.vm_vnfm_director_details(Server_details, ccd1)

        log.info('vmvnfm director ip : %s and vmvnfm username : %s', vm_vnfm_director_ip, vm_vnfm_director_username)
        director_connection = ServerConnection.get_nested_server_connection(
            ecm_connection,
            ecm_server_ip,
            vm_vnfm_director_ip,
            vm_vnfm_director_username,
            file_path,
        )
        return director_connection

    except Exception as e:
        log.info('Error connecting with VM-VNFM host server %s', str(e))
        assert False


def get_testhotel_vmvnfm_host_connection(vm_vnfm_director_ip, vm_vnfm_director_username):
    """
    Connect with Test Hotel CCD Director.
    @param vm_vnfm_director_ip: It is CCD Director IP
    @param vm_vnfm_director_username: It is CCD director username
    @return director_connection: It returns the ccd director connection
    """
    try:
        log.info('Start connecting with Test Hotel VM-VNFM host server ')
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        file_path = 'ccd-c3a002.director.pem'
        ServerConnection.get_file_sftp(ecm_connection, '/root/' + file_path, file_path)

        director_connection = ServerConnection.get_nested_server_connection(
            ecm_connection,
            ecm_server_ip,
            vm_vnfm_director_ip,
            vm_vnfm_director_username,
            file_path,
        )

        return director_connection

    except Exception as e:

        log.info('Error connecting with VM-VNFM host server %s', str(e))
        Report_file.add_line('Error connecting with VM-VNFM host server ' + str(e))
        assert False


def get_director_server_connection(ccd1):
    try:
        log.info('Start connecting with Director server ')
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        (
            directory_server_ip,
            directory_server_username,
        ) = Server_details.vm_vnfm_director_details(Server_details, ccd1)

        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        file_path = 'eccd-2-3.pem'

        director_server_connection = ServerConnection.get_nested_server_connection(
            ecm_connection,
            ecm_server_ip,
            directory_server_ip,
            directory_server_username,
            file_path, )

        return director_server_connection

    except Exception as e:

        log.info('Error connecting with Director server %s', str(e))
        Report_file.add_line('Error connecting with Director server ' + str(e))
        assert False


def transfer_director_file_to_vm_vnfm(dir_connection, source, destination):
    """this method is used to transfer files and folders both from director server to pod"""
    try:
        log.info('Transfer from director path {} to VM_VNFM path {}'.format(source, destination))
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)

        command = '''kubectl cp {} eric-vnflcm-service-0:{} -n {}'''.format(
            source, destination, vm_vnfm_namespace)
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = dir_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(command_output)
        Report_file.add_line('command_output : ' + command_output)

    except Exception as e:

        log.info('Error transferring file from director server to VM-VNFM %s', str(e))
        Report_file.add_line('Error transferring file from director server to VM-VNFM ' + str(e))
        assert False


def chown_and_file_permission(dir_connection, folder, permission, owner):
    """
    Change the permission and ownership of the folder in vnflcm
    Input:
        folder: Folder to change ownership or permission
        owner: Ownership (Jboss_user/eric-vnflcm-service)
        permission: file read, write, execute permission(755,777)
        folder_depth: increment if parent folder permission also required to change
    """
    try:
        log.info('start setting permission and ownership of file %s to %s, %s', folder, permission, owner)
        vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
        command = (f'kubectl exec '
                   f'-it eric-vnflcm-service-0 '
                   f'-c eric-vnflcm-service -n {vm_vnfm_namespace} '
                   f'-- bash -c "sudo python '
                   f'/opt/ericsson/ERICvnflcmservicecontainer_CXP9037964/bin/set_permissions.py --path {folder} '
                   f'--permission {permission} --user {owner} --recursive"')

        log.info('Executing command %s', command)
        stdin, stdout, stderr = dir_connection.exec_command(command, get_pty=True)
        handle_stderr(stderr, log)
        log.info('setting permission and ownership of file %s to %s, %s completed', folder, permission, owner)
    except Exception as error:
        log.info('Failed to set permission and ownership of file %s to %s, %s', folder, permission, owner)
        assert False


def get_file_from_vm_vnfm(dir_connection, source, destination):
    try:
        # source : /vnflcm-ext/current/vnf_package_repo/hot
        # destination : /home/eccd/hot
        log.info('Transfer from VM_VNFM path {} to director path {}'.format(source, destination))
        Report_file.add_line('Transfer from VM_VNFM path {} to director path {}'.format(source, destination))

        command = '''kubectl cp eric-vnflcm-service-0:{} {} -n {}'''.format(
            source, destination, vm_vnfm_namespace)
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = dir_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(command_output)
        Report_file.add_line('command_output : ' + command_output)

    except Exception as e:

        log.info('Error transfering file from VM_VNFM server to director %s', str(e))
        Report_file.add_line('Error transfering file from VM_VNFM server to director' + str(e))
        assert False


def get_file_name_from_vm_vnfm(dir_connection, extention, path):
    try:
        log.info('fetching file name with extention {} from path {}'.format(extention, path))
        Report_file.add_line('fetching file name with extention {} from path {}'.format(extention, path))

        command = '''kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c "cd {};ls -ltr | grep -i {}"'''.format(
            vm_vnfm_namespace, path, extention)
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = dir_connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        Report_file.add_line('command_output : ' + command_output)
        file_name = output[-1][:-3]
        log.info('file  name ' + file_name)

        return file_name

    except Exception as e:

        log.info('Error fetching file from VM_VNFM server to director %s', str(e))
        Report_file.add_line('Error fetching file from VM_VNFM server to director' + str(e))
        assert False


def get_file_name_from_director_server(dir_connection, extention, path):
    try:
        log.info('fetching file name with extention {} from path {}'.format(extention, path))
        Report_file.add_line('fetching file name with extention {} from path {}'.format(extention, path))

        command = 'cd {};ls -ltr | grep -i {}'.format(path, extention)
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = dir_connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        Report_file.add_line('command_output : ' + command_output)
        file_name = output[-1][:-3]
        log.info('file  name ' + file_name)

        return file_name

    except Exception as e:

        log.info('Error fetching file name from director server %s', str(e))
        Report_file.add_line('Error fetching file name from director server' + str(e))
        assert False


def run_command_vm_vnfm_db(dir_connection, db_command, db_name):
    """ this is method can we used to run any command on vm_vnfm db
    returns command output for verification
    dir_connection -- nested connection with vm vnfm director server
    db command  -- TRUNCATE vims cascade;
    db_name -- vnflafdb
    """
    try:
        vmvnfm_version = fetch_vmvnfm_version(dir_connection, vm_vnfm_namespace)
        log.info('run command %s in database %s', db_command, db_name)
        interact = dir_connection.invoke_shell()

        master_pod = get_master_vnflcm_db_pod(dir_connection)
        command = f'kubectl exec -it {master_pod} -n {vm_vnfm_namespace} /bin/bash'
        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if vmvnfm_version >= version.parse("2.29.0-3"):
            command = f'psql -U postgres -d {db_name}'
        else:
            if 'postgres@' not in buff:
                command = 'su postgres'
                interact.send(command + '\n')
                time.sleep(3)
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
            command = f'psql -d {db_name}'

        interact.send(command + '\n')
        time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if db_name in buff:
            interact.send(db_command + '\n')
            time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        return buff

    except Exception as e:

        log.info('Error running command in vm vnfm db %s', str(e))
        assert False


def edit_value_in_file(connection, filepath, key, new_value, filename):
    try:
        log.info('Start to edit the key value %s', key)
        Report_file.add_line('Start to edit the key value ' + key)
        command = f'''cd {filepath} ; sed -i '/'{key}'/c\      \'{key}'\:{new_value},' {filename}'''
        Report_file.add_line('command to get file  : ' + command)
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())

        Report_file.add_line('command output : ' + command_output)
    except Exception as e:
        log.error('Error While updating the value')
        Report_file.add_line('Error While updating the value')
        assert False


def change_file_permission_on_pod(connection, pod, container, namespace, filepath):
    try:
        command = 'kubectl exec -it {} -c {} -n {} -- bash -c "chown root:root {}"'.format(
            pod, container, namespace, filepath)
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())
        command = '''kubectl exec -it {} -c {} -n {} -- bash -c "chmod 777 {}"'''.format(
            pod, container, namespace, filepath)
        Report_file.add_line('command to get file  : ' + command)
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())
        Report_file.add_line('command output : ' + command_output)
    except Exception as e:
        log.error('Failed to change the file permission')
        Report_file.add_line('Failed to change the file permission')
        assert False


def get_master_vnflcm_db_pod(connection):
    try:
        log.info('Start to get master vnflcm db pod')
        Report_file.add_line('Start to get master vnflcm db pod')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        awk_command = "'{print $1}'"
        command = f'''kubectl get pods -L role -n {vm_vnfm_namespace} | grep -i 'eric-vnflcm-db' | grep -i 'master' | awk {awk_command} '''
        Report_file.add_line('Command - ' + command)

        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        master_pod = command_output[2:-3:1]

        Report_file.add_line('Master pod value - ' + master_pod)
        if master_pod != '':
            return master_pod
        else:
            log.info('VNFLCM db master pod not found ')
            Report_file.add_line('VNFLCM db master pod not found ')
            assert False

    except Exception as e:
        log.error('Error while getting the master vnflcm db pod %s', str(e))
        Report_file.add_line('Error while getting the master vnflcm db pod ' + str(e))
        assert False


def transfer_file_to_pod_db(pod, namespace, dir_connection, source, destination):
    try:
        log.info('Transfer file from director path {} to VM_VNFM path {}'.format(source, destination))
        Report_file.add_line(
            'Transfer file from director path {} to VM_VNFM path '.format(source, destination))

        command = '''kubectl -n {} cp {} {}:{}'''.format(namespace, source, pod, destination)

        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = dir_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(command_output)
        Report_file.add_line('command_output : ' + command_output)

    except Exception as e:

        log.info('Error while transferring file from director server to VM-VNFM %s', str(e))
        Report_file.add_line('Error while transferring file from director server to VM-VNFM ' + str(e))
        assert False


def change_file_permissions_of_file_on_pod_db(pod, namespace, dir_connection, filename, path):
    try:
        log.info('Start to Change file permissions on pod database')
        Report_file.add_line('Start to Change file permissions on pod database')
        command = 'kubectl -n {} exec -it {} -- bash -c "cd {};chmod 777 {}"'.format(
            namespace, pod, path, filename)
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = dir_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(command_output)
        Report_file.add_line('command_output : ' + command_output)

    except Exception as e:

        log.info('Error while changing file permissions on pod %s', str(e))
        Report_file.add_line('Error while changing file permissions on pod' + str(e))
        assert False


def fetch_vmvnfm_version(connection, vm_vnfm_namespace):
    try:
        log.info("start fetching vmvnfm version")
        command = 'kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c ' \
                  '"vnflcm version"'.format(vm_vnfm_namespace)
        stdin, stdout, stderr = connection.exec_command(command)
        command_out = stdout.read().decode("utf-8").split("\n")
        log.info("command_output: %s", command_out)
        vmvnfm_version = [res.split(':')[1].strip() for res in command_out if 'vmvnfm version' in res][0]
        if isinstance(version.parse(vmvnfm_version), version.Version):
            log.info("vmvnfm version is: %s", vmvnfm_version)
            return version.parse(vmvnfm_version)
        else:
            log.error('Invalid vmvnfm version: %s', vmvnfm_version)
            assert False
    except Exception as error:
        log.error('Failed to fetch vmvnfm version: %s', str(error))
        assert False
