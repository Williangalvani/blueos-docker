<template>
  <v-card>
    <v-card-title class="text-h5 grey lighten-2 black--text">
      {{ extension? extension.name : '' }}
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
            <v-select
              :items="available_tags"
              label="Standard"
            />
            <h4 v-if="extension && extension.website">
              Website:
            </h4>
            <a :href="extension ? extension.website : null">
              {{ extension ? extension.website : '' }}</a>
            <h4 v-if="extension && extension.docs">
              Docs:
            </h4>
            <a :href="extension ? extension.docs : null">
              {{ extension ? extension.docs : '' }}</a>

            <h4>Permissions:</h4>
            <v-card
              width="100%"
            >
              <v-card-text>
                <pre>{{ extension ? extension.permissions: '' }}</pre>
              </v-card-text>
            </v-card>
            <h4>Authors:</h4>
            <v-card>
              <v-card-text>
                <ul>
                  <li
                    v-for="author in (extension ? extension.authors : [])"
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
</template>

<script lang="ts">
import { marked } from 'marked'
import Vue, { PropType } from 'vue'

import { ExtensionData } from '@/types/kraken'
import back_axios from '@/utils/api'

export default Vue.extend({
  name: 'ExtensionModal',
  props: {
    extension: {
      type: Object as PropType<ExtensionData | null>,
      required: false,
    },
  },
  computed: {
    compiled_markdown(): string {
      if (this.extension?.readme === undefined || this.extension?.readme === null) {
        return 'No readme available'
      }
      return marked(this.extension?.readme, { sanitize: true })
    },
    available_tags(): string[] {
      if (this.extension && this.extension.versions) {
        const keys = Object.keys(this.extension.versions)
        return keys ?? []
      }
      return []
    },
  },

})
</script>
