# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
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

        # Apply baseline template
        template = ncs.template.Template(branch_service_node)
        for device in service.topology.device:
            vars = ncs.template.Variables()
            vars.add('DEVICE-NAME', device.name)
            vars.add('SERVICE-NAME', service.name)
            template.apply('wan-router-base-asr-template', vars)

        # Apply Interface Policies
        try:
            for connection in service.topology.connection:
                self.log.info('Connection: ', connection.name, ' ', connection._path)
                for endpoint in connection.endpoint:
                    vars = ncs.template.Variables()
                    vars.add('SERVICE-NAME', service.name)
                    vars.add('DEVICE-NAME', endpoint.device)
                    vars.add('INTERFACE-NAME', endpoint.interface_name)
                    self.log.info('Endpoint: ', endpoint.number, ' ', endpoint._path, ' ', endpoint.interface_name)
                    for connectionpolicy in endpoint.policy:
                        self.log.info('Policy: ', connectionpolicy, ' ', type(connectionpolicy))
#                        self.log.info('Endpoint.Policy Class: ', type(endpoint.policy), ' ', endpoint.policy._path)
                        policynode = ncs.maagic.cd(endpoint.policy,connectionpolicy)
                        if policynode is not None:
#                        self.log.info('policynode: ', type(policynode))
                            policynodetemplatestr = '/branch:branch-service/branch:branch-policies/branch:interface/'+connectionpolicy+'{"'+policynode+'"}/template'
                            self.log.info('Policy Node: ', policynodetemplatestr)
                            policy_template_name = ncs.maagic.cd(root, policynodetemplatestr)
                            self.log.info('APPLY TEMPLATE: Device: ', endpoint.device, ' Interface: ', endpoint.interface_name, ' Template: ', policy_template_name)
                            template.apply(policy_template_name, vars)
        except AttributeError as error:
            self.log.info('No Interface Policies to Apply')
            self.log.info(error)


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

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Deploy FINISHED')
