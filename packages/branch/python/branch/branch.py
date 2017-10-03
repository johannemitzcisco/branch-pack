# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from ncs.dp import Action
from ncs.maapi import Maapi
#from ncs.maapi import Transaction


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ' ', service.name, ')')
        branch_service_node = service._parent._parent

        # Apply device baseline templates
        template = ncs.template.Template(branch_service_node)
        for device in service.topology.device:
            vars = ncs.template.Variables()
            vars.add('SERVICE-NAME', service.name)
            vars.add('DEVICE-TOPOLOGY-NAME', device.topology_name)
            vars.add('DEVICE-NAME', device.hostname)
            if device.hostname not in root.devices.device: # The device is not yet registered with NSO
                for registration_policy in device.policies.registration:
                    self.log.info('Registration Policy: ', registration_policy.policy_name)
                    policynodetemplatestr = '/branch:branch-service/branch:branch-policies/branch:device/registration{"'+str(registration_policy.policy_name)+'"}/template'
                    self.log.info('Policy Template Location: ', policynodetemplatestr)
                    policy_template_name = ncs.maagic.cd(root, policynodetemplatestr)
                    self.log.info('APPLY TEMPLATE: Device: ', device.hostname, ' Template: ', policy_template_name)
                    template.apply(policy_template_name, vars)
                continue
            devicerole = device.type.role
            devicemodel = device.type.model
            vars.add('DEVICE-ROLE', str(devicerole))
            self.log.info('======= Device =============')
            self.log.info('Device Role : ', str(devicerole), ' ', type(devicerole))
            self.log.info('Device Model : ', devicemodel, ' ', type(devicemodel))
            basetemplatestr = '/branch:branch-service/branch:branch-policies/branch:device/branch:role{"'+str(devicerole)+'"}/model{"'+devicemodel+'"}/template'
            self.log.info('Device Template Path: ', basetemplatestr)
            device_base_template = ncs.maagic.cd(root, basetemplatestr)
            self.log.info('APPLY TEMPLATE: Device:', device.hostname, ' Template: ', device_base_template)
            template.apply(device_base_template, vars)
            self.log.info('======= Device Role Policies =============')
            role_policies_str = '/branch:branch-service/branch:branch-policies/branch:device/branch:role{"'+str(devicerole)+'"}/policies'
            self.log.info('Device Role Policies String : ', role_policies_str)
            role_policies = ncs.maagic.cd(root, role_policies_str)
            for policy_list in role_policies:
                self.log.info('Policy List: ', policy_list, ' Type: ', type(policy_list))
                policy_list_name_str = '/branch:branch-service/branch:branch-policies/branch:device/branch:role{"'+str(devicerole)+'"}/policies/'+policy_list
                self.log.info('Device Role Policy List Name String : ', policy_list_name_str)
                policy_list_name = ncs.maagic.cd(root, policy_list_name_str)
                self.log.info('Policy Name: ', policy_list_name, ' Type: ', type(policy_list_name))
                if policy_list_name is not None:
                    for policy in policy_list_name:
                        policy_template_str = '/branch:branch-service/branch:branch-policies/branch:device/'+str(policy_list)+'{'+policy+'}/template'
                        self.log.info('Device Policy Template String : ', policy_template_str)
                        policy_template = ncs.maagic.cd(root, policy_template_str)
                        self.log.info('APPLY TEMPLATE: Device:', device.hostname, ' Template: ', policy_template, ' Type: ', type(policy_template))
                        vars.add('POLICY-NAME', policy)
                        template.apply(policy_template, vars)
            self.log.info('======= Device Specific Policies =============')
            for policy in device.policies:
                try:
                    if policy != 'registration': #This is a special policy that should only be applied when the device does not exist
                        policylistnode = ncs.maagic.cd(device.policies,policy)
                        self.log.info('Policy: ', policy, ' ', type(policy), ' node type: ', type(policylistnode), ' DICT:',policylistnode.__dict__)
                        self.log.info('PolicyNodeKeys: ', policylistnode.keys())
                        policynames =  set([str(policykeys[0]) for policykeys in policylistnode.keys()])
                        self.log.info('PolicyNames: ', policynames)
                        for policyname in policynames:
                            self.log.info('Policy Name: ', policyname)
                            vars.add('POLICY-NAME', policyname)
                            policynodetemplatestr = '/branch:branch-service/branch:branch-policies/branch:device/'+str(policy)+'{"'+str(policyname)+'"}/template'
                            self.log.info('Policy Template Location: ', policynodetemplatestr)
                            policy_template_name = ncs.maagic.cd(root, policynodetemplatestr)
                            self.log.info('APPLY TEMPLATE: Device: ', device.hostname, ' Template: ', policy_template_name)
                            template.apply(policy_template_name, vars)
                except AttributeError as error:
                    self.log.info('Ignoring: ', error)
        # Apply Interface Policies
        self.log.info('======= Connections =============')
        for connection in service.topology.connection:
            vars = ncs.template.Variables()
            vars.add('SERVICE-NAME', service.name)
            self.log.info('Connection: ', connection.name, ' Path: ', connection._path)
            for connectiontype in connection.type:
                connectiontypenode = ncs.maagic.cd(connection.type,connectiontype)
                self.log.info('Connection Type: ', connectiontype, ' ', type(connectiontypenode))
                try:
                    if connectiontypenode is not None and connectiontypenode.policy_name is not None:
                        self.log.info('Policy Name: ', connectiontypenode.policy_name, ' ', type(connectiontypenode))
                        break
                except AttributeError as error:
                    pass
            for side in ('A', 'B'):
                if side in connection.side:
                    side_device = connection.side[side].device
                    if side_device not in root.devices.device: # The device is not yet registered with NSO
                        continue
                    vars.add('DEVICE-NAME', side_device)
                    vars.add('CONNECTION-NAME', connection.name)
                    if side_device is not None:
                        side_device_role_location = '/branch:branch-service/branch:branch{'+service.name+'}/branch:topology/branch:device{'+side_device+'}/branch:type/branch:role'
                        self.log.info('Side Device: ', side_device, ' Location: ', side_device_role_location)
                        side_device_role = ncs.maagic.cd(root, side_device_role_location)
                        self.log.info('Device role: ', side_device_role)
                        policynodetemplatestr = '/branch:branch-service/branch:branch-policies/branch:connection/'+connectiontype+'{"'+connectiontypenode.policy_name+'"}/branch:'+str(side_device_role)+'/branch:template'
                        self.log.info('Policy Node: ', policynodetemplatestr)
                        policy_template_name = ncs.maagic.cd(root, policynodetemplatestr)
                        self.log.info('APPLY TEMPLATE: Device: ', side_device, ' Template: ', policy_template_name)
                        template.apply(policy_template_name, vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

class LoadServiceTemplate(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        self.log.info('Branch Name: ', input.branch_name)
        self.log.info('template: ', input.topology_template)
        self.log.info('Keypath: ', kp)
        self.log.info('SELF WT: ', type(self._wt), ' ', dir(self._wt))
        # Updating the output data structure will result in a response
        # being returned to the caller.
        template = input.topology_template
        m = ncs.maapi.Maapi()
        m.start_user_session(uinfo.username, uinfo.context)
        t = m.start_write_trans()
        template_name = ncs.maagic.get_node(t, "/branch:branch-service/branch-policies/branch/topology-templates{"+input.topology_template+"}/model-template-file")
        self.log.info('Branch Template Name: ', template_name)
        vars = ncs.template.Variables()
        vars.add('BRANCH-NAME',input.branch_name)
        m.apply_template(t.th,name=template_name,path=kp,vars=vars)
        try:
            pass
        finally:
            t.finish_trans()
            m.close()



# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Deploy(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Deploy RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('branch-servicepoint', ServiceCallbacks)
        self.register_action('loadservicetemplate-action', LoadServiceTemplate)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Deploy FINISHED')
