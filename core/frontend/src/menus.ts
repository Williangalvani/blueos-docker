const menus = [
  {
    title: 'Autopilot Firmware',
    icon: 'mdi-image-filter-center-focus-strong',
    route: '/vehicle/autopilot',
    advanced: false,
    text: 'Update flight controller firmware, select the active autopilot,'
      + ' and start/stop ArduPilot (if using Navigator or SITL).',
  },
  {
    title: 'Autopilot Parameters',
    icon: 'mdi-table-settings',
    route: '/vehicle/parameters',
    text: 'View and modify vehicle parameters.',
  },
  {
    title: 'Available Services',
    icon: 'mdi-account-hard-hat',
    route: '/tools/available-services',
    advanced: true,
    text: 'List all available services found in BlueOS serving http interfaces, and their'
      + ' respective API documentations.',
  },
  {
    title: 'Bag Editor',
    icon: 'mdi-code-json',
    route: '/tools/bag-editor',
    advanced: true,
    text: 'Editor for Bag Of Holding service.',
  },
  {
    title: 'BlueOS Version',
    icon: 'mdi-cellphone-arrow-down',
    route: '/tools/version-chooser',
    advanced: false,
    text: 'Manage BlueOS versions and update to the latest available.',
  },
  {
    title: 'File Browser',
    icon: 'mdi-file-tree',
    route: '/tools/file-browser',
    advanced: true,
    text: 'Browse all the files in BlueOS. Useful for fetching logs,'
      + ' tweaking configurations, and development.',
  },
  {
    title: 'Log Browser',
    icon: 'mdi-math-log',
    route: '/vehicle/logs',
    advanced: false,
    text: 'Allow browsing the Telemetry (.tlog) and Binary (.bin) logs generated by your vehicle. Bin logs are'
      + ' currently only supported for Navigator boards.',
  },
  {
    title: 'MAVLink Endpoints',
    icon: 'mdi-arrow-decision',
    route: '/vehicle/endpoints',
    advanced: true,
    text: 'Manage MAVLink endpoints for internal/external systems. Use this if you need to connect additional'
      + ' MAVLink systems to your vehicle.',
  },
  {
    title: 'MAVLink Inspector',
    icon: 'mdi-chart-areaspline',
    route: '/tools/mavlink-inspector',
    advanced: true,
    text: 'View detailed MAVLink traffic coming from your vehicle.',
  },
  {
    title: 'NMEA Injector',
    icon: 'mdi-map-marker',
    route: '/tools/nmea-injector',
    advanced: true,
    text: 'Used for forwarding UDP NMEA streams into ArduPilot.',
  },
  {
    title: 'Network Test',
    icon: 'mdi-speedometer',
    route: '/tools/network-test',
    show: true,
    text: 'Test link speed between topside computer and your vehicle.',
  },
  {
    title: 'Ping Sonar Devices',
    icon: 'mdi-radar',
    route: '/vehicle/pings',
    advanced: false,
    text: 'Manage detected Ping family sonar devices, connected to either your Onboard Computer'
      + ' or its local network.',
  },
  {
    title: 'Serial Bridges',
    icon: 'mdi-bridge',
    route: '/tools/bridges',
    advanced: true,
    text: 'Allows creating UDP/TCP to Serial bridges, used for communication to serial'
      + ' devices from your Control Station Computer.',
  },
  {
    title: 'System Information',
    icon: 'mdi-chart-pie',
    route: '/tools/system-information',
    advanced: false,
    text: 'Detailed system status information, CPU, memory, disk, and ethernet status.',
  },
  {
    title: 'Terminal',
    icon: 'mdi-console',
    route: '/tools/web-terminal',
    advanced: true,
    text: 'A web-based console. Used mainly for debugging and development.',
  },
  {
    title: 'Vehicle Setup',
    icon: 'mdi-cog-outline',
    route: '/vehicle/setup',
    advanced: false,
    text: 'Vehicle and Peripherals setup. Includes sensor calibrations and Motors/Peripherals mapping.',
  },
  {
    title: 'Video Streams',
    icon: 'mdi-video-vintage',
    route: '/vehicle/video-manager',
    advanced: false,
    text: 'Manage your video devices and video streams.',
  },
  {
    title: 'Zenoh Inspector',
    icon: 'mdi-chart-areaspline',
    route: '/tools/zenoh-inspector',
    advanced: true,
    text: 'View detailed Zenoh traffic coming from your vehicle.',
  },
] as menuItem[]

export interface menuItem {
  title: string,
  icon: string,
  text?: string, // Option description

  advanced?: boolean, // The option will only be enable in pirate mode
  beta?: boolean, // Used on menus that are in development
  extension?: boolean, // True if is an extension
  new_page?: string, // The address will open in a new page
  route?: string, // The option routes to a different address
  submenus?: menuItem[], // Menus that the main option provide
  disabled?: boolean, // The option is disabled
}

export default menus
