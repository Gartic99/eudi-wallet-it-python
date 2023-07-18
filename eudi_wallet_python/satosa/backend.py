import json
import logging
import base64

from six import text_type
from satosa.exception import SATOSAAuthenticationError
from satosa.response import Response
from satosa.backends.base import BackendModule

logger = logging.getLogger(__name__)


class OpenIDVP4SAMLBackend(BackendModule):
    """
    A saml2 backend module (acting as a OpenIDVP4 SP).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.qrCode_url = self.config['qrCode_enpoint']
        self.redirect_url = self.config['redirect_endpoint']
        self.request_url = self.config['request_enpoint']

    def register_endpoints(self):
        """
        Creates a list of all the endpoints this backend module needs to listen to. In this case
        it's the authentication response from the underlying OP that is redirected from the OP to
        the proxy.
        :rtype: Sequence[(str, Callable[[satosa.context.Context], satosa.response.Response]]
        :return: A list that can be used to map the request to SATOSA to this endpoint.
        """
        url_map = []
        url_map.append((f"^{self.qrCode_url.lstrip('/')}$", self.qrCode_endpoint))
        url_map.append((f"^{self.redirect_url.lstrip('/')}$", self.redirect_endpoint))
        url_map.append((f"^{self.request_url.lstrip('/')}$", self.request_enpoint))
        return url_map
    
    def qrCode_endpoint(self, context, *args):
        return Response(
            text_type(
                base64.b64encode(bytes('eudiw://authorize?client_id=https://verifier.example.org&request_uri=https://verifier.example.org/request_uri', 'UTF-8'))
            ).encode("utf-8"), content="text/xml; charset=utf8"
        )
    
    def redirect_endpoint(self, context, *args):
        return Response(
            text_type(
                base64.encode('')
            ).encode("utf-8"), content="text/xml; charset=utf8"
        )
    
    def request_enpoint(self, context, *args):
        return Response(
            text_type(
                base64.encode('')
            ).encode("utf-8"), content="text/xml; charset=utf8"
        )

    def _metadata_endpoint(self, context):
        """
        Endpoint for retrieving the backend metadata
        :type context: satosa.context.Context
        :rtype: satosa.response.Response

        :param context: The current context
        :return: response with metadata
        """
        logger.debug("Sending metadata response")
        self.sp.config

        """metadata = entity_descriptor(conf)
        
        # metadata signature
        secc = security_context(conf)
        #
        sign_dig_algs = self.get_kwargs_sign_dig_algs()
        eid, xmldoc = sign_entity_descriptor(
            metadata, None, secc, **sign_dig_algs)

        valid_instance(eid)"""
        return Response(
            text_type("").encode("utf-8"), content="text/xml; charset=utf8"
        )

    def get_kwargs_sign_dig_algs(self):
        kwargs = {}
        # backend support for selectable sign/digest algs
        alg_dict = dict(signing_algorithm="sign_alg",
                        digest_algorithm="digest_alg")
        for alg in alg_dict:
            selected_alg = self.config["sp_config"]["service"]["sp"].get(alg)
            if not selected_alg:
                continue
            kwargs[alg_dict[alg]] = selected_alg
        return kwargs

    def check_blacklist(self, context, entity_id):
        # If IDP blacklisting is enabled and the selected IDP is blacklisted,
        # stop here
        if self.idp_blacklist_file:
            with open(self.idp_blacklist_file) as blacklist_file:
                blacklist_array = json.load(blacklist_file)["blacklist"]
                if entity_id in blacklist_array:
                    logger.debug(
                        "IdP with EntityID {} is blacklisted".format(entity_id)
                    )
                    raise SATOSAAuthenticationError(
                        context.state, "Selected IdP is blacklisted for this backend"
                    )

    def authn_request(self, context, entity_id):
        """
        Do an authorization request on idp with given entity id.
        This is the start of the authorization.

        :type context: satosa.context.Context
        :type entity_id: str
        :rtype: satosa.response.Response

        :param context: The current context
        :param entity_id: Target IDP entity id
        :return: response to the user agent
        """

    def handle_error(
        self,
        message: str,
        troubleshoot: str = "",
        err="",
        template_path="templates",
        error_template="spid_login_error.html",
    ):
        """
        Todo: Jinja2 tempalte loader and rendering :)
        """
        logger.error(f"Failed to parse authn request: {message} {err}")
        result = self.error_page.render(
            {"message": message, "troubleshoot": troubleshoot}
        )
        return Response(result, content="text/html; charset=utf8", status="403")


    def authn_response(self, context, binding):
        """
        Endpoint for the idp response
        :type context: satosa.context,Context
        :type binding: str
        :rtype: satosa.response.Response

        :param context: The current context
        :param binding: The saml binding type
        :return: response
        """
