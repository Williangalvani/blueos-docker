<template>
  <v-container>
    <v-dialog
      v-model="show_dialog"
      width="80%"
    >
      <v-card>
        <v-card-title class="text-h5 grey lighten-2 black--text">
          {{ selected_extension? selected_extension.name : '' }}
        </v-card-title>

        <v-card-text>
          <v-row>
            <v-col
              cols="10"
              sm="8"
              class="mt-5"
            >
              <v-card
                min-height="50vh"
                rounded="lg"
                style="overflow: auto;"
              >
                <v-card-text>
                  <div
                    class="readme"
                    v-html="compiled_markdown"
                  />
                </v-card-text>
              </v-card>
            </v-col>
            <v-col
              cols="4"
              sm="4"
              class="mt-5"
            >
              <v-sheet
                min-height="50vh"
                rounded="lg"
              >
                <h4 v-if="selected_extension && selected_extension.website">
                  Website:
                </h4>
                <a :href="selected_extension ? selected_extension.website : null">
                  {{ selected_extension ? selected_extension.website : '' }}</a>
                <h4 v-if="selected_extension && selected_extension.docs">
                  Docs:
                </h4>
                <a :href="selected_extension ? selected_extension.docs : null">
                  {{ selected_extension ? selected_extension.docs : '' }}</a>

                <h4>Permissions:</h4>
                <v-card
                  width="100%"
                >
                  <v-card-text>
                    <pre>{{ selected_extension ? selected_extension.permissions: '' }}</pre>
                  </v-card-text>
                </v-card>
                <h4>Authors:</h4>
                <v-card>
                  <v-card-text>
                    <ul>
                      <li
                        v-for="author in (selected_extension ? selected_extension.authors : [])"
                        :key="author.email"
                      >
                        {{ author.name }}
                      </li>
                    </ul>
                  </v-card-text>
                </v-card>
              </v-sheet>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="justify-center">
          <v-btn
            color="primary"
          >
            Install
          </v-btn>
        </v-card-actions>
      </v-card>
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
      <v-row>
        <div
          v-for="extension in manifest"
          :key="extension.website+extension.tag"
          class="pa-2"
        >
          <v-card
            class="mx-auto"
            width="300"
            outlined
            style="cursor: pointer;"
            @click="showModal(extension)"
          >
            <v-list-item three-line>
              <v-list-item-avatar
                tile
                size="50"
                color="grey"
              />
              <v-list-item-content>
                <v-list-item-title
                  class="text-h5 mb-1 extension-name"
                  style="font-size: 18px !important;"
                >
                  {{ extension.name }}
                </v-list-item-title>
                <v-list-item-subtitle> {{ extension.description }} </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-card-subtitle class="pt-0">
              {{ extension.author }}
            </v-card-subtitle>
          </v-card>
        </div>
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
  </v-container>
</template>

<script lang="ts">
import { marked } from 'marked'
import Vue from 'vue'

import Notifier from '@/libs/notifier'
import { kraken_service } from '@/types/frontend_services'
import back_axios from '@/utils/api'

import { ExtensionData } from '../types/kraken'

const API_URL = '/kraken/v1.0'

const notifier = new Notifier(kraken_service)

export default Vue.extend({
  name: 'ExtensionManagerView',
  data() {
    return {
      tab: 0,
      show_dialog: false,
      selected_extension: null as (null | ExtensionData),
      // TODO: fetch this from backend
      manifest: [] as ExtensionData[],
    }
  },
  computed: {
    compiled_markdown(): string {
      if (this.selected_extension?.readme === undefined || this.selected_extension?.readme === null) {
        return 'No readme available'
      }
      return marked(this.selected_extension?.readme, { sanitize: true })
    },
  },
  mounted() {
    this.fetchManifest()
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
    showModal(extension: ExtensionData) {
      this.show_dialog = true
      this.selected_extension = extension
    },
  },
})
</script>

<style>
  div.readme h1 {
    margin: 5px;
  }
</style>
