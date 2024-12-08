import asyncio
from typing import List, Optional

from commonwealth.utils.general import is_running_as_root
from serial.tools.list_ports_linux import SysFS, comports

from flight_controller_detector.board_identification import get_board_ids_from_usb_id, load_board_identifiers
from flight_controller_detector.linux.detector import LinuxFlightControllerDetector
from typedefs import FlightController, FlightControllerFlags, Platform, PlatformType
from loguru import logger


class Detector:
    @classmethod
    async def detect_linux_board(cls) -> Optional[FlightController]:
        for _i in range(5):
            board = cls._detect_linux_board()
            if board:
                return board
            await asyncio.sleep(0.1)
        return None

    @classmethod
    def _detect_linux_board(cls) -> Optional[FlightController]:
        """Returns Linux board if connected.
        Check for connection using the sensors on the I²C and SPI buses.

        Returns:
            Optional[FlightController]: Return FlightController if connected, None otherwise.
        """
        return LinuxFlightControllerDetector.detect_boards()

    @staticmethod
    def is_serial_bootloader(port: SysFS) -> bool:
        return port.product is not None and "BL" in port.product

    @staticmethod
    def detect_serial_platform(port: SysFS) -> list[Platform]:
        vid = port.vid
        pid = port.pid

        # Check if vid and pid are not None before formatting
        if vid is None or pid is None:
            return []

        usb_id = f"{vid:04x}:{pid:04x}"
        platforms = []
        identifiers = load_board_identifiers()
        if usb_id in identifiers:
            for board_platform in identifiers[usb_id]:
                platforms.append(Platform(name=board_platform, platform_type=PlatformType.Serial))
        return platforms

    @staticmethod
    def detect_serial_flight_controllers() -> List[FlightController]:
        """Check if a standalone flight controller is connected via usb/serial.

        Returns:
            List[FlightController]: List with connected serial flight controller.
        """
        sorted_serial_ports = sorted(comports(), key=lambda port: port.name)  # type: ignore
        unique_serial_devices: List[SysFS] = []
        for port in sorted_serial_ports:
            # usb_device_path property will be the same for two serial connections using the same USB port
            if port.usb_device_path not in [device.usb_device_path for device in unique_serial_devices]:
                unique_serial_devices.append(port)

        boards = []
        for port in unique_serial_devices:
            platforms = Detector.detect_serial_platform(port)
            logger.info(f"platforms: {platforms}")
            for platform in platforms:
                board_name = port.product or port.name

                # Get board_id using USB VID:PID
                board_id = None
                if port.vid is not None and port.pid is not None:
                    board_ids = get_board_ids_from_usb_id(port.vid, port.pid, board_name)
                    if len(board_ids) > 1:
                        logger.warning(f"Multiple board_ids found for {board_name}. using {board_ids[0]}")
                        board_id = board_ids[0]
                    elif len(board_ids) == 1:
                        board_id = board_ids[0]

                logger.info(f"creating FlightController: {platform} {board_name} {port.device} {board_id}")
                board = FlightController(
                    name=board_name,
                    manufacturer=port.manufacturer,
                    platform=platform,
                    path=port.device,
                    ardupilot_board_id=board_id,
                )
                boards.append(board)
        for port in unique_serial_devices:
            for board in boards:
                if board.path == port.device and Detector.is_serial_bootloader(port):
                    board.flags.append(FlightControllerFlags.is_bootloader)
        # if we have multiple boards with the same name, lets keep the one with the shortest platform name
        if len(boards) > 1:
            logger.info(f"multiple boards with the same name: {boards}. keeping the shortest platform name")
            boards = sorted(boards, key=lambda x: len(x.platform.name))
            return boards[:1]
        logger.info(f"detected serial boards: {boards}")
        return boards

    @staticmethod
    def detect_sitl() -> FlightController:
        return FlightController(name="SITL", manufacturer="ArduPilot Team", platform=Platform.SITL())

    @classmethod
    async def detect(cls, include_sitl: bool = True, include_manual: bool = True) -> List[FlightController]:
        """Return a list of available flight controllers

        Arguments:
            include_sitl {bool} -- To include or not SITL controllers in the returned list

        Returns:
            List[FlightController]: List of available flight controllers
        """
        available: List[FlightController] = []

        available.extend(cls().detect_serial_flight_controllers())

        if include_sitl:
            available.append(Detector.detect_sitl())

        if include_manual:
            available.append(
                FlightController(
                    name="Manual",
                    manufacturer="Manual",
                    platform=Platform(name="Manual", platform_type=PlatformType.Serial),
                    path="",
                    ardupilot_board_id=None,
                )
            )

        if not is_running_as_root():
            return available

        linux_board = await cls.detect_linux_board()
        if linux_board:
            available.append(linux_board)

        return available
