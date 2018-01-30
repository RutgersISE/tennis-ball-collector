import platform

from .localization import TargetLocator, AgentLocator, watch_onboard, watch_offboard
if platform.uname()[4][:3] == 'arm':
    from .cameras import CalibratedPicamera as Camera
else:
    from .cameras import CalibratedCamera as Camera

