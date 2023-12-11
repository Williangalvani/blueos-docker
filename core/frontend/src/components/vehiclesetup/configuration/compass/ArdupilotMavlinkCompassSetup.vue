<template>
  <v-card>
    <div class="d-flex flex-row">
      <v-card outline class="pa-2 mt-4 mr-2 mb-2">
        <compass-display :compasses="compasses_sorted_by_priority" />
      </v-card>
      <v-card outline class="pa-2 mt-4 mr-2 mb-2">
        <v-card-title>
          <h3>Global Compass Settings</h3>
        </v-card-title>
        <v-card-text>
          <div class="d-flex flex-row">
            <v-card class="pa-2 ma-2">
              <h4>CompassLearn</h4>
              <p> This allows automatic "calibration" of compass offsets. You need to have a valid world position.</p>
              <p>
                In order to use this option, click the following button and then driver the vehicle around until you
                see the message "CompassLearn: finished"
              </p>
              <v-btn disabled color="primary">
                Enable Compass Learn
              </v-btn>
            </v-card>
            <v-card class="pa-2 ma-2">
              <h4>Declination</h4>
              <v-switch label="Auto Declination" />
              <p>
                If you enable this option, the autopilot will automatically set the declination based on your current
                location.
              </p>
              <v-text-field label="Declination" disabled :value="printParam(compass_dec)" />
            </v-card>
          </div>
          <div class="d-flex flex-row">
            <v-card class="pa-2 ma-2" disabled>
              <h4>Compass Calibration</h4>
              <p>
                This does a full calibration of the compasses.
                It requires you to spin the vehicle around manually multiple times.
                You need move the vehicle around in all 3 axis.
              </p>
              <v-btn disabled color="primary">
                Run Full Calibration
              </v-btn>
            </v-card>
            <v-card class="pa-2 ma-2">
              <h4>Large Vehicle Calibration</h4>
              <p>
                This does a "quick" calibration of your compass.
                You need to point your vehicle North, and then click the button.
                This results in a much less accurate calibration, but is also much faster.
                It can be a good starting point for calibration, followed by CompassLearn.
              </p>
              <large-vehicle-compass-calibrator :compasses="compasses" />
            </v-card>
          </div>
        </v-card-text>
      </v-card>
    </div>
    <div class="d-flex flex-row">
      <v-tabs v-model="tab" vertical color="primary">
        <draggable v-model="reordered_compasses" handle=".drag-handle">
          <v-tab
            v-for="compass in reordered_compasses"
            :key="compass.deviceName"
            class="pl-0 pr-0 compass-tab pt-4 pb-4 mt-4 mb-4"
            outline
          >
            <v-icon start class="mr-2 mt-3 mb-3 drag-handle">
              mdi-drag-vertical
            </v-icon>
            <v-icon start class="mr-2" :style="`color:${compassColors[compass.deviceIdNumber - 1]}`">
              mdi-compass
            </v-icon>
            <div class="d-flex flex-column pa-3">
              {{ compass.deviceName }} <br />
              {{ compass_description[compass.param] }}
              <v-chip
                v-if="compass_is_calibrated[compass.param]"
                color="green"
                text-color="white"
                x-small
                class="calibration-chip"
              >
                Calibrated
              </v-chip>
              <v-chip v-else color="red" text-color="white" x-small>
                Needs Calibration
              </v-chip>
            </div>
            <v-icon end>
              mdi-cog
            </v-icon>
          </v-tab>
        </draggable>
        <v-tab-item
          v-for="(compass, index) in compasses"
          v-show="tab === index"
          :key="index"
          transition="v-scroll-y-transition"
        >
          <v-card outlined class="pa-2 mt-4 compass-settings">
            <v-card-title>
              <h3>{{ compass.deviceName }}</h3>
            </v-card-title>
            <v-row>
              <v-col cols="6">
                <v-card class="pa-5">
                  <h4>Details</h4>
                  <p>Bus: 0x{{ compass.address }} @ {{ compass.busType }}{{ compass.bus }} </p>
                </v-card>
                <v-card class="pa-5 mt-3">
                  <h4>Settings</h4>
                  Mounting Rotation: {{ printParam(compass_orient_param[compass.param]) }}
                  <v-icon end @click="openParameterEditor(compass_orient_param[compass.param])">
                    mdi-pencil
                  </v-icon>
                  <br />
                  External/Internal: {{ printParam(compass_extern_param[compass.param]) }}
                  <v-icon end @click="openParameterEditor(compass_extern_param[compass.param])">
                    mdi-pencil
                  </v-icon>
                </v-card>
              </v-col>
              <v-col cols="6">
                <compass-params :index="index + 1" />
              </v-col>
            </v-row>
          </v-card>
        </v-tab-item>
      </v-tabs>
    </div>
    <parameter-editor-dialog
      v-model="edit_param_dialog"
      :param="edited_param"
    />
  </v-card>
</template>
<script lang="ts">
import Vue from 'vue'
import draggable from 'vuedraggable'
import { VTextField } from 'vuetify/lib'

import CompassDisplay from '@/components/vehiclesetup/configuration/compass/CompassDisplay.vue'
import CompassParams from '@/components/vehiclesetup/configuration/compass/CompassParams.vue'
import mavlink2rest from '@/libs/MAVLink2Rest'
import autopilot_data from '@/store/autopilot'
import Parameter, { printParam } from '@/types/autopilot/parameter'
import { Dictionary } from '@/types/common'
import decode, { deviceId } from '@/utils/deviceid_decoder'

import LargeVehicleCompassCalibrator from './LargeVehicleCompassCalibrator.vue'

export default Vue.extend({
  name: 'MavlinkCompassSetup',
  components: {
    CompassDisplay,
    CompassParams,
    draggable,
    VTextField,
    LargeVehicleCompassCalibrator,
  },
  data() {
    return {
      tab: 0,
      compassColors: ['red', 'green', 'blue'],
      reordered_compasses: [] as deviceId[],
      edited_param: undefined as (undefined | Parameter),
      edit_param_dialog: false,
    }
  },
  computed: {
    compass_learn(): Parameter | undefined {
      return autopilot_data.parameter('COMPASS_LEARN')
    },
    compass_autodec(): Parameter | undefined {
      return autopilot_data.parameter('COMPASS_AUTODEC')
    },
    compass_dec(): Parameter | undefined {
      return autopilot_data.parameter('COMPASS_DEC')
    },
    compass_use(): Parameter | undefined {
      return autopilot_data.parameter('COMPASS_USE')
    },
    compasses(): deviceId[] {
      return autopilot_data.parameterRegex('^COMPASS_DEV_ID.*')
        .filter((param) => param.value !== 0)
        .map((parameter) => decode(parameter.name, parameter.value))
    },
    compass_priority(): Dictionary<number> {
      const results = {} as Dictionary<number>
      for (const compass of this.compasses) {
        // First we check the priority for this device
        for (const param of autopilot_data.parameterRegex('^COMPASS_PRIO.*_ID')) {
          if (param.value === compass.paramValue) {
            const number_in_parameter_as_string = param.name.match(/\d+/g)?.[0] ?? '1'
            results[compass.param] = parseInt(number_in_parameter_as_string, 10)
          }
        }
      }
      return results
    },
    compasses_sorted_by_priority(): deviceId[] {
      const sortedCompasses = [...this.compasses]
      sortedCompasses.sort((a, b) => this.compass_priority[a.param] - this.compass_priority[b.param])
      return sortedCompasses
    },
    compass_description(): Dictionary<string> {
      const results = {} as Dictionary<string>
      for (const compass of this.compasses) {
        // First we check the priority for this device
        let priority = 'Unused'
        let number_in_parameter = 0
        for (const param of autopilot_data.parameterRegex('^COMPASS_PRIO.*_ID')) {
          if (param.value === compass.paramValue) {
            const number_in_parameter_as_string = param.name.match(/\d+/g)?.[0] ?? '1'
            number_in_parameter = parseInt(number_in_parameter_as_string, 10)
            switch (number_in_parameter) {
              case 1:
                priority = '1st'
                break
              case 2:
                priority = '2nd'
                break
              case 3:
                priority = '3rd'
                break
              default:
                priority = 'Unused'
            }
          }
        }
        // Then we check if it is internal or external
        const extern_param_name = number_in_parameter === 1
          ? 'COMPASS_EXTERNAL' : `COMPASS_EXTERN${number_in_parameter}`
        const external = autopilot_data.parameter(extern_param_name)?.value === 1 ?? false
        const external_string = external ? 'external' : 'internal'
        results[compass.param] = `${priority} (${external_string})`
      }
      return results
    },
    compass_is_calibrated(): Dictionary<boolean> {
      const results = {} as Dictionary<boolean>
      for (const compass of this.compasses) {
        const compass_number = compass.param.split('COMPASS_DEV_ID')[1]
        const offset_params_names = [
          `COMPASS_OFS${compass_number}_X`,
          `COMPASS_OFS${compass_number}_Y`,
          `COMPASS_OFS${compass_number}_Z`,
        ]
        const diagonal_params_names = [
          `COMPASS_ODI${compass_number}_X`,
          `COMPASS_ODI${compass_number}_Y`,
          `COMPASS_ODI${compass_number}_Z`,
        ]

        const offset_params = offset_params_names.map(
          (name) => autopilot_data.parameter(name),
        )
        const diagonal_params = diagonal_params_names.map(
          (name) => autopilot_data.parameter(name),
        )
        if (offset_params.includes(undefined) || diagonal_params.includes(undefined)) {
          results[compass.param] = false
          continue
        }
        const scale_param_name = `COMPASS_SCALE${compass_number}`
        const scale_param = autopilot_data.parameter(scale_param_name)
        const is_at_default_offsets = offset_params.every((param) => param?.value === 0.0)
        const is_at_default_diagonals = diagonal_params.every((param) => param?.value === 0.0)
        results[compass.param] = offset_params.isEmpty() || diagonal_params.isEmpty()
          || !is_at_default_offsets || !is_at_default_diagonals || scale_param?.value !== 0.0
      }
      return results
    },
    compass_orient_param(): Dictionary<Parameter> {
      const results = {} as Dictionary<Parameter>
      for (const compass of this.compasses) {
        const compass_number = compass.param.split('COMPASS_DEV_ID')[1]
        const param = autopilot_data.parameter(`COMPASS_ORIENT${compass_number}`)
        if (param) {
          results[compass.param] = param
        }
      }
      return results
    },
    compass_extern_param(): Dictionary<Parameter> {
      const results = {} as Dictionary<Parameter>
      for (const compass of this.compasses) {
        const compass_number = compass.param.split('COMPASS_DEV_ID')[1]
        const param_name = compass_number ? `COMPASS_EXTERN${compass_number}` : 'COMPASS_EXTERNAL'
        const param = autopilot_data.parameter(param_name)
        if (param) {
          results[compass.param] = param
        }
      }
      return results
    },
  },
  watch: {
    compasses_sorted_by_priority() {
      if (this.reordered_compasses.isEmpty()) {
        this.reordered_compasses = this.compasses_sorted_by_priority
      }
    },
    reordered_compasses() {
      const compasses = this.reordered_compasses
      for (const [index, compass] of compasses.entries()) {
        const param_name = `COMPASS_PRIO${index + 1}_ID`
        const param = autopilot_data.parameter(param_name)
        if (param?.value !== compass.paramValue) {
          mavlink2rest.setParam(param_name, compass.paramValue, autopilot_data.system_id)
          autopilot_data.setRebootRequired(true)
        }
      }
    },
  },
  mounted() {
    this.reordered_compasses = this.compasses_sorted_by_priority
  },
  methods: {
    printParam,
    openParameterEditor(parameter: Parameter | undefined) {
      if (parameter) {
        this.edited_param = parameter
        this.edit_param_dialog = true
      }
    },
  },
})
</script>
<style scoped>
.chip-container {
  display: flex;
  flex-direction: column; /* Change the flex-direction to column */
  align-items: flex-start; /* Align items to the start */
}
.compass-tab.v-tab--active {
  border-bottom:  1px solid var(--v-primary-base);
  border-top: 1px solid var(--v-primary-base);
  border-left:  1px solid var(--v-primary-base);
  border-radius: 5px 0 0 5px;
  transform: translateX(5px);
}
.compass-tab {
  min-height: 70px;
}

.calibration-chip {
  margin: auto;
}

.compass-settings {
  border-color: var(--v-primary-base);
}
</style>
