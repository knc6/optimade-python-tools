import urllib

from typing import Union

from fastapi import APIRouter, Request
from fastapi.exceptions import StarletteHTTPException

from optimade import __api_version__
from optimade.server.config import CONFIG
from optimade.models import (
    ErrorResponse,
    InfoResponse,
    EntryInfoResponse,
)

from .utils import (
    meta_values,
    retrieve_queryable_properties,
    get_base_url,
    ENTRY_INFO_SCHEMAS,
)


router = APIRouter(redirect_slashes=True)


@router.get(
    "/info",
    response_model=Union[InfoResponse, ErrorResponse],
    response_model_exclude_unset=True,
    tags=["Info"],
)
def get_info(request: Request):
    from optimade.models import BaseInfoResource, BaseInfoAttributes

    parse_result = urllib.parse.urlparse(str(request.url))
    base_url = get_base_url(parse_result)

    return InfoResponse(
        meta=meta_values(str(request.url), 1, 1, more_data_available=False),
        data=BaseInfoResource(
            id=BaseInfoResource.schema()["properties"]["id"]["const"],
            type=BaseInfoResource.schema()["properties"]["type"]["const"],
            attributes=BaseInfoAttributes(
                api_version=f"v{__api_version__}",
                available_api_versions=[
                    {
                        "url": f"{base_url}/v{__api_version__.split('.')[0]}",
                        "version": __api_version__,
                    }
                ],
                formats=["json"],
                available_endpoints=["info", "links"] + list(ENTRY_INFO_SCHEMAS.keys()),
                entry_types_by_format={"json": list(ENTRY_INFO_SCHEMAS.keys())},
                is_index=False,
            ),
        ),
    )


@router.get(
    "/info/{entry}",
    response_model=Union[EntryInfoResponse, ErrorResponse],
    response_model_exclude_unset=True,
    tags=["Info"],
)
def get_entry_info(request: Request, entry: str):
    from optimade.models import EntryInfoResource

    valid_entry_info_endpoints = ENTRY_INFO_SCHEMAS.keys()
    if entry not in valid_entry_info_endpoints:
        raise StarletteHTTPException(
            status_code=404,
            detail=f"Entry info not found for {entry}, valid entry info endpoints are: {valid_entry_info_endpoints}",
        )

    schema = ENTRY_INFO_SCHEMAS[entry]()
    queryable_properties = {"id", "type", "attributes"}
    entry_provider_fields = CONFIG.provider_fields.get(entry)
    properties = retrieve_queryable_properties(
        schema, queryable_properties, entry_provider_fields=entry_provider_fields
    )

    output_fields_by_format = {"json": list(properties.keys())}

    return EntryInfoResponse(
        meta=meta_values(str(request.url), 1, 1, more_data_available=False),
        data=EntryInfoResource(
            formats=list(output_fields_by_format.keys()),
            description=schema.get("description", "Entry Resources"),
            properties=properties,
            output_fields_by_format=output_fields_by_format,
        ),
    )
