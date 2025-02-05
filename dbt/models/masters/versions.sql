select
    versions_code as version_code,
    versions_name as version_name,
    is_active
from {{ source("masters", "versions") }}
