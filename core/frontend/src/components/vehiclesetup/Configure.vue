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
        <param-sets v-if="page.value === 'parameters'" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

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
  },
  data() {
    return {
      page_selected: null as string | null,
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
})
</script>
