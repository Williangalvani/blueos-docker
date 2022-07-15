import { Baudrate } from '@/types/common'

export interface PingDeviceInterface {
  ping_type: string,
  device_id: number,
  device_model: number,
  device_revision: number,
  firmware_version_major: number,
  firmware_version_minor: number,
  firmware_version_patch: number,
  port: string,
}

export class PingDevice implements PingDeviceInterface {
  constructor(
    public readonly ping_type: string,
    public readonly device_id: number,
    public readonly device_model: number,
    public readonly device_revision: number,
    public readonly firmware_version_major: number,
    public readonly firmware_version_minor: number,
    public readonly firmware_version_patch: number,
    public readonly port: string,
  ) {}

  fw_version(): string {
    return `${this.firmware_version_major}.${this.firmware_version_minor}.${this.firmware_version_patch}`
  }
}
