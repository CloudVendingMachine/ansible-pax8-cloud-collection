#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Dima Munkov <dmunkov@pax8.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: dmunkovpax8.cloud.github_oauth

short_description: This module is used to generate a GitHub OAuth token for a GitHub App.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "2.14.1"

description: This module is used to generate a GitHub OAuth token for a GitHub App.

options:
    owner:
        description: Repository owner or organization name.
        required: true
        type: str
    repository_name:
        description: Repository name. Required if scope is set to 'repository' which is default.
        required: false
        type: str
    application_id:
        description: GitHub App ID.
        required: true
        type: str
    scope:
        description: GitHub App permissions scope (default: 'repository').
        required: false
        default: 'repository'
        choices:
            - 'repository'
            - 'organization'
        type: str

    private_key:
        description: GitHub App private key.
        required: true
        type: str

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Dima Munkov (@dmunkovpax8)

requirements:
    - github>=1.59.0
'''

EXAMPLES = r'''
# Generate GitHub OAuth token for specific repository
- name: Generate GitHub OAuth token
  dmunkovpax8.cloud.github_oauth:
    owner: dmunkovpax8
    repository_name: ansible-github-oauth
    application_id: 12345
    scope: repository  # Optional parameter, default value is 'repository'
    private_key: |
        -----BEGIN RSA PRIVATE KEY-----
        
        -----END RSA PRIVATE KEY-----

# Generate GitHub OAuth token for the entire organization
- name: Generate GitHub OAuth token
  dmunkovpax8.cloud.github_oauth:
    owner: dmunkovpax8
    application_id: 12345
    scope: organization
    private_key: |
        -----BEGIN RSA PRIVATE KEY-----
        
        -----END RSA PRIVATE KEY-----
'''

RETURN = r'''
# Returned values
access_token:
    description: GitHub OAuth token.
    type: str
    returned: always
    sample: 'ghs_HysH5RENwrFsKcP2PmNAQmv52Sm6gt3kZsNU'
'''

from ansible.module_utils.basic import AnsibleModule
from github import GithubIntegration, Auth


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        owner=dict(type='str', required=True),
        repository_name=dict(type='str', required=False),
        application_id=dict(type='str', required=True, no_log=True),
        scope=dict(type='str', required=False, default='repository', choices=['repository', 'organization']),
        private_key=dict(type='str', required=True, no_log=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        token=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # if module.check_mode:
    #     module.exit_json(**result)

    # Create a GitHub integration object
    integration = GithubIntegration(auth=Auth.AppAuth(app_id=module.params['application_id'], private_key=module.params['private_key']))

    # Get an installation access token
    if module.params['scope'] == 'organization':
        installation_id = integration.get_org_installation(module.params['owner'])
    else:
        installation_id = integration.get_repo_installation(module.params['owner'], module.params['repository_name'])
    access_token = integration.get_access_token(installation_id.id).token

    result['token'] = access_token

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
