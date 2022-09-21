<template>
  <v-container>
    <v-dialog
      v-model="show_dialog"
      width="auto"
    >
    <vue-markdown :source="dialog_content">
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
      <div
        v-for="extension in manifest"
        :key="extension.website"
        class="pa-2"
        style="min-height: 100%;"
      >
        <v-card
          class="mx-auto"
          max-width="344"
          outlined
        >
          <v-list-item three-line>
            <v-list-item-avatar
              tile
              size="50"
              color="grey"
            />
            <v-list-item-content>
              <v-list-item-title class="text-h5 mb-1">
                {{ extension.name }}
              </v-list-item-title>
              <v-list-item-subtitle> {{ extension.description }} </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-card-actions>
            <v-btn
              outlined
              rounded
              text
            >
              Install
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
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
import Vue from 'vue'
import VueMarkdown from 'vue-markdown-render'

export default Vue.extend({
  name: 'ExtensionManagerView',
  components: {
    VueMarkdown
  },
  data() {
    return {
      tab: 0,
      show_dialog: true,
      dialog_content: 'asdassadsadadsadasdasdads',
      // TODO: fetch this from backend
      manifest: [

      ],
    }
  },
  mounted() {
    console.log('AEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
  },
})
</script>
