<template>
  <div>
    <v-card class="ml-10 mr-10 mt-4">
      <v-card-title>
        <h4>Select compasses to calibrate </h4>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <div v-for="(device, index) in devices" :key="device.id">
              <v-checkbox
                v-model="selected_devices[index]"
                dense
                :label="device.deviceName"
                :value="device.id"
                :background-color="getCompassColor(device.deviceIdNumber - 1)"
              />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'CompassMaskPicker',
  model: {
    prop: 'bitmask',
    event: 'input',
  },
  props: {
    devices: {
      type: Array,
      required: true,
      default: () => [],
    },
  },
  data() {
    return {
      selected_devices: [],
      new_bitmask: 0,
      compass_colors: ['#FFCCCC', '#CCFFCC', '#CCCCFF'],
    }
  },
  watch: {
    selected_devices() {
      this.new_bitmask = this.selected_devices.reduce((acc, val, index) => {
        if (val) {
          acc |= 1 << index
        }
        return acc
      }, 0)
      console.log(this.new_bitmask)
      this.$emit('input', this.new_bitmask)
    },
  },
  methods: {
    getCompassColor(index) {
      return this.compass_colors[index % this.compass_colors.length]
    },
  },
}
</script>
