<template>
  <v-app>
    <v-content>
      <FileUpload/>
    </v-content>
  </v-app>
</template>

<script>
import FileUpload from './components/FileUpload'

export default {
  name: 'App',

  components: {
    FileUpload
  }
}
</script>
