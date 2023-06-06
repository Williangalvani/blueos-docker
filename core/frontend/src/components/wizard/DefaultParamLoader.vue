<template>
  <v-card class="ma-2 pa-2">
    <v-card-title class="align-center">
      Load Default Parameters

      {{ board }} - {{ vehicle }} - {{ version }}
    </v-card-title>
    <v-card-text>
      <v-btn
        v-for="(paramSet, name) in filtered_param_sets"
        :key="name"
        color="primary"
        @click="setParamSet(paramSet); log(paramSet)"
      >
        {{ name.split('/').pop() }}
      </v-btn>
      <p v-if="(Object.keys(filtered_param_sets).length === 0)">
        No parameters available for this setup
      </p>
      {{ value }}
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { SemVer } from 'semver'
import Vue, { PropType } from 'vue'
import { Dictionary } from 'vue-router/types/router'

import mavlink2rest from '@/libs/MAVLink2Rest'
import autopilot from '@/store/autopilot_manager'
import { Firmware, FlightController, Vehicle } from '@/types/autopilot'
import { callPeriodically, stopCallingPeriodically } from '@/utils/helper_functions'

import { availableFirmwares, fetchCurrentBoard } from '../autopilot/AutopilotManagerUpdater'

const REPOSITORY_URL = 'https://williangalvani.github.io/Blueos-Parameter-Repository/params_v1.json'

export default Vue.extend({
  name: 'DefaultParamLoader',
  props: {
    value: {
      type: Object,
      default: () => ({}),
    },
    vehicle: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    all_param_sets: {} as Dictionary<Dictionary<number>>,
    version: undefined as (undefined | SemVer),
  }),
  computed: {
    filtered_param_sets(): Dictionary<Dictionary<number>> | undefined {
      const fw_patch = `${this.vehicle}/${this.version}/${this.board}`
      const fw_minor = `${this.vehicle}/${this.version?.major}.${this.version?.minor}/${this.board}`
      const fw_major = `${this.vehicle}/${this.version?.major}/${this.board}`

      // returns a new dict where the keys start with the fullname
      // e.g. "ArduSub/BlueROV2/4.0.3" -> "ArduSub/BlueROV2/4.0.3/BlueROV2"

      let fw_params = {}
      // try to find a paramset that matches the firmware version, starting from patch and walking up to major
      for (const string of [fw_patch, fw_minor, fw_major]) {
        fw_params = Object.fromEntries(
          Object.entries(this.all_param_sets).filter(
            ([name]) => name.toLocaleLowerCase().includes(string.toLowerCase()),
          ),
        )
        if (Object.keys(fw_params).length > 0) {
          break
        }
      }
      return {
        ...fw_params,
      }
    },
    board(): string | undefined {
      return autopilot.current_board?.name
    },
  },
  watch: {
    vehicle() {
      this.updateLatestFirmwareVersion().then((version: string) => {
        this.version = new SemVer(version.split('-')[1])
      })
    },
  },
  mounted() {
    this.loadParamSets()
    callPeriodically(fetchCurrentBoard, 10000)
  },
  beforeDestroy() {
    stopCallingPeriodically(fetchCurrentBoard)
  },
  methods: {
    updateLatestFirmwareVersion() {
      return availableFirmwares(this.vehicle as Vehicle)
        .then((firmwares: Firmware[]) => {
          const found: Firmware | undefined = firmwares.find((firmware) => firmware.name.includes('STABLE'))
          if (found === undefined) {
            return `Failed to find a stable version for vehicle (${this.vehicle})`
          }
          return found.name
        })
    },
    log(a: any) {
      console.log(a)
    },
    setParamSet(paramSet: Dictionary<number>) {
      this.$emit('input', paramSet)
    },
    async loadParamSets() {
      // fetch json file from https://williangalvani.github.io/Blueos-Parameter-Repository/params.json
      // and parse it into a dictionary
      const response = await fetch(REPOSITORY_URL)
      const paramSets = await response.json()
      this.all_param_sets = paramSets
    },
  },
})
</script>
