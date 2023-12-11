<template>
  <v-dialog
    v-model="dialog"
    width="500"
  >
    <template #activator="{ on, attrs }">
      <v-btn
        color="primary"
        v-bind="attrs"
        v-on="on"
      >
        Run Large Vehicle Calibration
      </v-btn>
    </template>

    <v-card>
      <v-card-title class="text-h5 grey lighten-2">
        Large Vehicle Compass Calibration
      </v-card-title>

      <v-card-text class="ma-3">
        A Broad position is required for large vehicle compass calibration.
        <br>
        <br>
        <v-icon dense :color="mavlink_lat ? 'green' : 'orange'">
          {{ mavlink_lat ? "mdi-check-circle" : "mdi-alert-circle" }}
        </v-icon>
        <b>GPS coordinates:</b> {{ mavlink_lat ?? "N/A" }} {{ mavlink_lon ?? "N/A" }}
        <br>
        <v-icon dense :color="geoip_lat ? 'green' : 'red'">
          {{ geoip_lat ? "mdi-check-circle" : "mdi-alert-circle" }}
        </v-icon>
        <b>GeoIP coordinates:</b> {{ geoip_lat ?? "N/A" }} {{ geoip_lon ?? "N/A" }}
        <br>
        <br>
        <b>Using:</b> {{ mavlink_lat ?? geoip_lat ?? 0 }} {{ mavlink_lon ?? geoip_lon ?? 0 }}
        <br>
        <br>
        Point your vehicle to <b>True North</b> and click <b>calibrate</b>.
        <compass-mask-picker v-model="compass_mask" :devices="compasses" />
      </v-card-text>
      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="calibrate()">
          Calibrate
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { PropType } from 'vue'

import mavlink2rest from '@/libs/MAVLink2Rest'
import { MavCmd } from '@/libs/MAVLink2Rest/mavlink2rest-ts/messages/mavlink2rest-enum'
import autopilot_data from '@/store/autopilot'
import { deviceId } from '@/utils/deviceid_decoder'

export default {
  name: 'LargeVehicleCompassCalibrator',
  props: {
    compasses: {
      type: Array as PropType<deviceId[]>,
      required: true,
    },
  },
  data() {
    return {
      dialog: false,
      mavlink_lat: undefined as number | undefined,
      mavlink_lon: undefined as number | undefined,
      geoip_lat: undefined as number | undefined,
      geoip_lon: undefined as number | undefined,
      compass_mask: 0,
    }
  },

  mounted() {
    mavlink2rest.startListening('GLOBAL_POSITION_INT').setCallback((receivedMessage) => {
      this.mavlink_lat = receivedMessage.message.lat !== 0 ? receivedMessage.message.lat : undefined
      this.mavlink_lon = receivedMessage.message.lon !== 0 ? receivedMessage.message.lon : undefined
    }).setFrequency(0)
    mavlink2rest.requestMessageRate('GLOBAL_POSITION_INT', 1, autopilot_data.system_id)
    this.getGeoIp()
  },
  methods: {
    calibrate() {
      this.largeVehicleCalibration(
        this.compass_mask,
        this.mavlink_lat ?? this.geoip_lat ?? 0,
        this.mavlink_lon ?? this.geoip_lon ?? 0,
      )
      this.$emit('close')
    },
    getGeoIp() {
      fetch('http://ip-api.com/json/')
        .then((response) => response.json())
        .then((data) => {
          this.geoip_lat = data.lat
          this.geoip_lon = data.lon
        })
        .catch((err) => console.error(err))
    },
    largeVehicleCalibration(compass_mask: number, lat: number, lon: number) {
      const payload = {
        header: {
          system_id: 255,
          component_id: 1,
          sequence: 1,
        },
        message: {
          type: 'COMMAND_LONG',
          param1: 0, // North
          param2: compass_mask,
          param3: parseInt(`${lat}`, 10),
          param4: parseInt(`${lon}`, 10),
          param5: 0,
          param6: 0,
          param7: 0,
          command: {
            type: MavCmd.MAV_CMD_FIXED_MAG_CAL_YAW,
          },
          target_system: autopilot_data.system_id,
          target_component: 1,
          confirmation: 0,
        },
      }
      console.log(payload)
      mavlink2rest.sendMessage(
        payload,
      )
    },
  },
}
</script>

<style scoped>

</style>
