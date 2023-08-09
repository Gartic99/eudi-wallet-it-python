import datetime
from pyeudiw.federation.trust_chain_validator import StaticTrustChainValidator

class BaseStorage(object):
    def init_session(self, document_id: str, dpop_proof: dict, attestation: dict):
        raise NotImplementedError()

    def update_request_object(self, document_id: str, nonce: str, state: str | None, request_object: dict):
        raise NotImplementedError()

    def update_response_object(self, nonce: str, state: str | None, response_object: dict):
        raise NotImplementedError()

    def find_chain(self, entityID: str):
        raise NotImplementedError()
        
    def has_chain(self, entityID: str):
        raise NotImplementedError()

    def add_chain(self, entityID: str, trust_chain: list[str], exp: datetime) -> str:
        raise NotImplementedError()
        
    def update_chain(self, entityID: str, trust_chain: list[str], exp: datetime) -> str:
        raise NotImplementedError()