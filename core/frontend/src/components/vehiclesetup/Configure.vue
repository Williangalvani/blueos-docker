<template>
  <v-container fluid>
    <v-tabs
      v-model="page_selected"
      centered
      show-arrows
    >
      <v-tabs-slider />
      <v-tab
        v-for="page in pages"
        :key="page.value"
      >
        {{ page.title }}
        <!-- <v-icon>{{ page.icon }}</v-icon> -->
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="page_selected">
      <v-tab-item
        v-for="page in pages"
        :key="page.value"
      >
        <param-sets v-if="page.value === 'parameters' && page.value === 'parameters'" />
        <template v-if="page.value === 'compass' && pages[page_selected ?? 0].value === 'compass'">
          <ardupilot-mavlink-compass-setup v-if="params_loaded" />
          <spinning-logo v-else size="30%" :subtitle="`${loaded_params}/${total_params} parameters loaded`" />
        </template>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

import autopilot_data from '@/store/autopilot'

import SpinningLogo from '../common/SpinningLogo.vue'
import ArdupilotMavlinkCompassSetup from './configuration/compass/ArdupilotMavlinkCompassSetup.vue'
import ParamSets from './overview/ParamSets.vue'

export interface Item {
  title: string,
  icon: string,
  value: string,
}

export default Vue.extend({
  name: 'Configure',
  components: {
    ParamSets,
    ArdupilotMavlinkCompassSetup,
    SpinningLogo,
  },
  data() {
    return {
      page_selected: null as number | null,
      pages: [
        { title: 'Parameters', value: 'parameters' },
        { title: 'Compass', value: 'compass' },
        { title: 'Baro', value: 'baro' },
        { title: 'Accelerometer', value: 'acc' },
        { title: 'Gripper', value: 'gripper' },
        { title: 'lights', value: 'lights' },
        { title: 'Camera Mount', value: 'mount' },

      ] as Item[],
    }
  },
  computed: {
    params_loaded(): boolean {
      return autopilot_data.finished_loading
    },
    loaded_params(): number {
      return autopilot_data.parameters_loaded
    },
    total_params(): number {
      return autopilot_data.parameters_total
    },
  },
})
</script>
