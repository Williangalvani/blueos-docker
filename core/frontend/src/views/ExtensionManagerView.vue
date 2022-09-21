<template>
  <v-container>
    <v-dialog
      v-model="show_dialog"
      width="auto"
    >
    <div v-html="compiled_markdown"></div>
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
import { marked } from 'marked'

export default Vue.extend({
  name: 'ExtensionManagerView',
  data() {
    return {
      tab: 0,
      show_dialog: true,
      dialog_content: 'asdassadsadadsadasdasdads',
      // TODO: fetch this from backend
      manifest: [
    {
        "name": "ZeroTier",
        "description": "ZeroTier integration",
        "docker": "williangalvani/zerotier",
        "website": "https://github.com/Williangalvani/ZeroTierOne",
        "permissions": "--net=host --device=/dev/net/tun --cap-add=NET_ADMIN --cap-add=SYS_ADMIN -v /var/lib/zerotier-one:/var/lib/zerotier-one",
        "requirements": "core >= 1",
        "tag": "latest",
        "version": null,
        "author": "Willian Galvani <willian@bluerobotics.com",
        "readme": "# This is a fork!\n\nThis was quickly put together in order to allow setting up ZeroTier on a BlueOS instance.\n\nTo install, do:\n\n`red-pill`\n\n`docker run -d --name zerotier-one --device=/dev/net/tun --net=host  --restart=unless-stopped   --cap-add=NET_ADMIN --cap-add=SYS_ADMIN   -v /var/lib/zerotier-one:/var/lib/zerotier-one williangalvani/zerotier`\n\n"
    },
    {
        "name": "WebRTC Experiments",
        "description": "Janus Gateway experiments",
        "docker": "williangalvani/companion-webrtc",
        "website": "https://github.com/Williangalvani/blueos-webrtc",
        "permissions": null,
        "requirements": null,
        "tag": "shift",
        "version": null,
        "author": "Willian Galvani <willian@bluerobotics.com",
        "readme": null
    },
    {
        "name": "WebRTC Experiments",
        "description": "Janus Gateway experiments",
        "docker": "williangalvani/companion-webrtc",
        "website": "https://github.com/Williangalvani/blueos-webrtc",
        "permissions": null,
        "requirements": null,
        "tag": "shift",
        "version": null,
        "author": "Willian Galvani <willian@bluerobotics.com",
        "readme": null
    },
    {
        "name": "Example 1",
        "description": "example 1",
        "docker": "williangalvani/blueos-example1",
        "website": "https://github.com/Williangalvani/BlueOS-examples/",
        "permissions": "--net=host",
        "requirements": null,
        "tag": "latest",
        "version": null,
        "author": "Willian Galvani <willian@bluerobotics.com",
        "readme": null
    },
    {
        "name": "USBIP",
        "description": "USBIP extension for extending USB over IP",
        "docker": "williangalvani/blueos-extension-usbip",
        "website": "https://github.com/Williangalvani/blueos-usbip",
        "permissions": null,
        "requirements": null,
        "tag": "latest",
        "version": null,
        "author": "Willian Galvani <willian@bluerobotics.com",
        "readme": "# USB/IP extension\n\nThis exposes usb devices via IP, which can be used in another client device\n\nTo use, first pull it in blueos:\n\n\n```\nred-pill\nsudo docker run -d --net=host --name=blueos-example1 --restart=unless-stopped williangalvani/blueos-extension-usbip:latest\n```\n\n# Client\n\n## Linux:\n\n\n```\n# load modules\nsudo modprobe usbip-core\nsudo modprobe vhci-hcd\n# list devices\nsudo usbip list --remote blueos.local\n# connect to device with bus 1-1.3\nsudo usbip attach --remote blueos.local --busid 1-1.3\n\n```\n\n## Windows\n\nDownload the 3.6 dev release from https://github.com/cezanne/usbip-win and follow the \"Client\" instructions there.\nThe new \"ude\" driver seemed to work for me."
    },
    {
        "name": "VirtualHere",
        "description": "VirtualHere extension for exposing USB devices over IP",
        "docker": "williangalvani/blueos-extension-virtualhere",
        "website": "https://github.com/Williangalvani/BlueOS-VirtualHere",
        "permissions": "--net=host --privileged",
        "requirements": "core > 1",
        "tag": "latest",
        "version": null,
        "author": "Willian Galvani <willian@bluerobotics.com",
        "readme": "# BlueOS VirtualHere extension\n\nThis exposes usb devices via IP, which can be used in another client device\n\nTo use, first install it in BlueOS:\n\n\n```\nred-pill\nsudo docker run -d --net=host --privileged --name=blueos-virtualhere --restart=unless-stopped williangalvani/blueos-extension-virtualhere:latest\n```\n\n# Client\n\nDownload a client from https://www.virtualhere.com/usb_client_software"
    },
    {
        "name": "Water Linked DVL Integration",
        "description": "BlueOS integration for Water Linked's DVLs",
        "docker": "bluerobotics/blueos-water-linked-dvl",
        "website": "https://github.com/bluerobotics/BlueOS-Water-Linked-DVL/",
        "permissions": null,
        "requirements": null,
        "tag": "latest",
        "version": null,
        "author": "Blue Robotics <software@bluerobotics.com>",
        "readme": "# BlueOS-Water-Linked-DVL\n\nThis is a docker implementation of a Waterlinked DVL-a50 driver for the new Blue Robotics BlueOS.\n\nTo set this up, ssh into the Raspberry Pi (or access via `red-pill` in [BlueOS Terminal](https://docs.bluerobotics.com/ardusub-zola/software/onboard/BlueOS-1.0/advanced-usage/#terminal)) and run\n\n`sudo docker run -d --net=host -v /root/.config/blueos:/root/.config --name=BlueOS-Water-Linked-DVL --restart=unless-stopped bluerobotics/blueos-water-linked-dvl:latest\n`\n\nThe service will show in the \"Available Services\" section in BlueOS, where there are some configuration options.\n"
    }
],
    }
  },
  mounted() {
    this.dialog_content = this.manifest[0].readme as string
  },
  computed: {
      compiledMarkdown () {
        return marked(this.dialog_content ?? '', { sanitize: true })
    },
  }
})
</script>
