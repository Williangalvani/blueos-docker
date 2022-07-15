<template>
  <v-container>
    <v-row
      class="mb-6 mt-6"
      justify="center"
      no-gutters
    />
    <v-card>
      <h2>Ping Devices</h2>
      <v-row>
        <v-col
          v-for="ping in ping_devices"
          :key="ping.device_id"
        >
          <v-card
            class="py-3 px-3"
            style="min-height: 100%; max-width: 30%;"
          >
            <h4>{{ ping.ping_type }}</h4>
            <v-simple-table dense>
              <tbody>
                <tr><td>ID</td><td>{{ ping.device_id }}</td></tr>
                <tr><td>Model</td><td>{{ ping.device_model }}</td></tr>
                <tr><td>Revision</td><td>{{ ping.device_revision }}</td></tr>
                <tr><td>Port</td><td>{{ ping.port }}</td></tr>
              </tbody>
            </v-simple-table>
          </v-card>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'

import ping from '@/store/ping'
import { PingDevice } from '@/types/ping'

export default Vue.extend({
  name: 'Peripherals',
  data: () => ({
  }),
  computed: {
    ping_devices(): PingDevice[] {
      return ping.available_ping_devices
    },
  },
})
</script>

<style scoped>
  .v-card {
    padding: 30px;
  }
</style>
