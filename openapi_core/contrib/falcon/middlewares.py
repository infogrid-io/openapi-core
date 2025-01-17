"""OpenAPI core contrib falcon middlewares module"""
from typing import Any
from typing import Optional
from typing import Type

from falcon.request import Request
from falcon.response import Response

from openapi_core.contrib.falcon.handlers import FalconOpenAPIErrorsHandler
from openapi_core.contrib.falcon.requests import FalconOpenAPIRequest
from openapi_core.contrib.falcon.responses import FalconOpenAPIResponse
from openapi_core.spec import Spec
from openapi_core.validation.processors import OpenAPIProcessor
from openapi_core.validation.request.datatypes import RequestValidationResult
from openapi_core.validation.request.protocols import RequestValidator
from openapi_core.validation.response.datatypes import ResponseValidationResult
from openapi_core.validation.response.protocols import ResponseValidator


class FalconOpenAPIMiddleware(OpenAPIProcessor):

    request_class = FalconOpenAPIRequest
    response_class = FalconOpenAPIResponse
    errors_handler = FalconOpenAPIErrorsHandler()

    def __init__(
        self,
        spec: Spec,
        request_validator_cls: Optional[Type[RequestValidator]] = None,
        response_validator_cls: Optional[Type[ResponseValidator]] = None,
        request_class: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_class: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler: Optional[FalconOpenAPIErrorsHandler] = None,
    ):
        super().__init__(
            spec,
            request_validator_cls=request_validator_cls,
            response_validator_cls=response_validator_cls,
        )
        self.request_class = request_class or self.request_class
        self.response_class = response_class or self.response_class
        self.errors_handler = errors_handler or self.errors_handler

    @classmethod
    def from_spec(
        cls,
        spec: Spec,
        request_validator_cls: Optional[Type[RequestValidator]] = None,
        response_validator_cls: Optional[Type[ResponseValidator]] = None,
        request_class: Type[FalconOpenAPIRequest] = FalconOpenAPIRequest,
        response_class: Type[FalconOpenAPIResponse] = FalconOpenAPIResponse,
        errors_handler: Optional[FalconOpenAPIErrorsHandler] = None,
    ) -> "FalconOpenAPIMiddleware":
        return cls(
            spec,
            request_validator_cls=request_validator_cls,
            response_validator_cls=response_validator_cls,
            request_class=request_class,
            response_class=response_class,
            errors_handler=errors_handler,
        )

    def process_request(self, req: Request, resp: Response) -> None:  # type: ignore
        openapi_req = self._get_openapi_request(req)
        req.context.openapi = super().process_request(openapi_req)
        if req.context.openapi.errors:
            return self._handle_request_errors(req, resp, req.context.openapi)

    def process_response(  # type: ignore
        self, req: Request, resp: Response, resource: Any, req_succeeded: bool
    ) -> None:
        openapi_req = self._get_openapi_request(req)
        openapi_resp = self._get_openapi_response(resp)
        resp.context.openapi = super().process_response(
            openapi_req, openapi_resp
        )
        if resp.context.openapi.errors:
            return self._handle_response_errors(
                req, resp, resp.context.openapi
            )

    def _handle_request_errors(
        self,
        req: Request,
        resp: Response,
        request_result: RequestValidationResult,
    ) -> None:
        return self.errors_handler.handle(req, resp, request_result.errors)

    def _handle_response_errors(
        self,
        req: Request,
        resp: Response,
        response_result: ResponseValidationResult,
    ) -> None:
        return self.errors_handler.handle(req, resp, response_result.errors)

    def _get_openapi_request(self, request: Request) -> FalconOpenAPIRequest:
        return self.request_class(request)

    def _get_openapi_response(
        self, response: Response
    ) -> FalconOpenAPIResponse:
        return self.response_class(response)
