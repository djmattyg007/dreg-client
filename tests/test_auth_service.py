from datetime import datetime

import pytest
from freezegun import freeze_time

from dreg_client.auth_service import AuthToken, DockerTokenAuthService, make_expires_at


@pytest.mark.parametrize(
    ("validity_duration", "expires_at"),
    (
        (-56, 1630644331),
        (-55, 1630644331),
        (-54, 1630644331),
        (-1, 1630644331),
        (0, 1630644331),
        (1, 1630644331),
        (42, 1630644331),
        (50, 1630644331),
        (53, 1630644331),
        (54, 1630644331),
        (55, 1630644331),
        (56, 1630644331),
        (59, 1630644331),
        (60, 1630644331),
        (61, 1630644332),
        (62, 1630644333),
        (90, 1630644361),
        (120, 1630644391),
        (300, 1630644571),
    ),
)
def test_make_expires_at(validity_duration: int, expires_at: int):
    time_dest = datetime.utcfromtimestamp(1630644276)
    with freeze_time(time_dest):
        actual = make_expires_at(validity_duration)
        assert actual == expires_at
