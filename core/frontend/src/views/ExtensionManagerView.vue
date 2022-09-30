<template>
  <v-container fluid>
    <v-dialog
      v-model="show_dialog"
      width="80%"
    >
      <extension-modal
        :extension="selected_extension"
        @clicked='install'
      />
    </v-dialog>
    <v-tabs
      v-model="tab"
      fixed-tabs
    >
      <v-tab>Installed</v-tab>
      <v-tab>Store</v-tab>
    </v-tabs>
    <div
      v-if="tab === 1"
      class="d-flex pa-5"
    >
      <v-row dense>
        <v-col
          v-for="extension in manifest"
          :key="extension.website "
          class="pa-2"
        >
          <extension-card
            :extension="extension"
            @clicked="showModal(extension)"
          />
        </v-col>
      </v-row>
      <v-container
        v-if="manifest.length === 0"
        class="text-center"
      >
        <p class="text-h6">
          No Extensions available.
        </p>
      </v-container>
    </div>
    <v-row>
      <v-col
        v-if="tab === 0"
        class="pa-5"
      >
        <v-row
          v-for="container in filtered_dockers"
          :key="container.id"
          dense
        >
          <v-col
            class="pa-2"
          >
            <v-card>
              <v-card-title>
                {{ container.name.replace('/', '') }}
              </v-card-title>
              <v-card-text>
                CPU:  {{ cpuUsage(container).toFixed(1) }}%
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-container
          v-if="dockers.length === 0"
          class="text-center"
        >
          <p
            v-if="dockers_fetch_done"
            class="text-h6"
          >
            No Extensions available.
          </p>
          <p
            v-else
            class="text-h6"
          >
            Fetching Extensions
          </p>
        </v-container>
      </v-col>
      <v-col
        v-if="tab === 0"
        class="pa-5 pt-6"
      >
        <v-card>
          <v-card-text>
            <v-checkbox
              v-model="show_all"
              :label="'Show unmananged'"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

import ExtensionCard from '@/components/kraken/ExtensionCard.vue'
import ExtensionModal from '@/components/kraken/ExtensionModal.vue'
import Notifier from '@/libs/notifier'
import { kraken_service } from '@/types/frontend_services'
import back_axios from '@/utils/api'
import axios from 'axios'

import { ExtensionData } from '../types/kraken'

const API_URL = '/kraken/v1.0'

const notifier = new Notifier(kraken_service)

export default Vue.extend({
  name: 'ExtensionManagerView',
  components: {
    ExtensionCard,
    ExtensionModal,
  },
  data() {
    return {
      tab: 0,
      show_dialog: false,
      selected_extension: null as (null | ExtensionData),
      // TODO: fetch this from backend
      manifest: [] as ExtensionData[],
      dockers: [] as any[],
      dockers_fetch_done: false,
      show_all: false as boolean,
    }
  },
  computed: {
    filtered_dockers() {
      return this.dockers.filter((docker: any) => docker.managed || this.show_all)
    },
  },
  mounted() {
    this.fetchManifest()
    this.fetchRunningDockers()
  },
  methods: {
    async fetchManifest(): Promise<void> {
      await back_axios({
        method: 'get',
        url: `${API_URL}/extensions_manifest`,
        timeout: 3000,
      })
        .then((response) => {
          const manifest = response.data
          this.manifest = manifest
        })
        .catch((error) => {
          notifier.pushBackError('EXTENSIONS_MANIFEST_FETCH_FAIL', error)
        })
    },
    cpuUsage(metric: any) {
      console.log(metric)
      var cpuDelta = metric.cpu_stats.cpu_usage.total_usage -  metric.precpu_stats.cpu_usage.total_usage;
      var systemDelta = metric.cpu_stats.system_cpu_usage - metric.precpu_stats.system_cpu_usage;
      return cpuDelta / systemDelta * 100;
    },
    async fetchRunningDockers(): Promise<void> {
      await back_axios({
        method: 'get',
        url: `${API_URL}/running_dockers`,
        timeout: 30000,
      })
        .then((response) => {
          const dockers = response.data
          this.dockers = dockers
          this.dockers_fetch_done = true
        })
        .catch((error) => {
          notifier.pushBackError('EXTENSIONS_MANIFEST_FETCH_FAIL', error)
        })
    },
    showModal(extension: ExtensionData) {
      this.show_dialog = true
      this.selected_extension = extension
    },
    async install(tag: str) {
      await axios.post(`${API_URL}/install_extension`, {
        name: this.selected_extension?.docker,
        tag: tag,
        enabled: true,
        permissions: JSON.stringify(this.selected_extension?.versions[tag].permissions)

      })
        .then((response) => {
          console.log("done")
          this.show_dialog = false
        })
        .catch((error) => {
          notifier.pushBackError('EXTENSIONS_MANIFEST_FETCH_FAIL', error)
        })
    },
    }
  },
})
</script>

<style>
  div.readme h1 {
    margin: 5px;
  }
</style>
