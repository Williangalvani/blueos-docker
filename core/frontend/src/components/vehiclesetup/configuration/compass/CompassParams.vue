<template>
  <div>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(parameter, index2) in compass_params " :key="index2">
          <td>{{ parameter.name }}</td>
          <td>{{ parameter.value }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import autopilot_data from '@/store/autopilot'
import Parameter from '@/types/autopilot/parameter'

export default {
  name: 'CompassParams',
  props: {
    index: {
      type: Number,
      required: true,
    },
  },
  computed: {
    str_index() {
      return this.index === 1 ? '' : this.index
    },
    compass_params(): Parameter[] {
      // Espcial case for EXTERN, which changes from EXTERNAL to EXTERN1, EXTERN2, etc.
      let extern = []
      if (this.str_index === '') {
        extern = autopilot_data.parameterRegex('^COMPASS_EXTERNAL')
      } else {
        extern = autopilot_data.parameterRegex(`^COMPASS_EXTERN${this.str_index}`)
      }

      const params = [
        ...autopilot_data.parameterRegex(`^COMPASS_DIA${this.str_index}_.*`),
        ...autopilot_data.parameterRegex(`^COMPASS_OFS${this.str_index}_.*`),
        ...autopilot_data.parameterRegex(`^COMPASS_ODI${this.str_index}_.*`),
        ...autopilot_data.parameterRegex(`^COMPASS_ORIENT${this.str_index}_.*`),
        ...autopilot_data.parameterRegex(`^COMPASS_USE${this.str_index}_.*`),
        ...autopilot_data.parameterRegex(`^COMPASS_MOT${this.str_index}_.*`),
        ...extern,
      ]
      return params
    },
  },
  created() {
    // Fetch your parameters here and assign them to this.parameters
  },
}
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #f2f2f2;
}
</style>
