<template>
  <GMapMap
    :center="center"
    :zoom="6"
    map-type-id="terrain"
    class="w-full rounded-lg"
    style="height: 20rem"
    :options="options"
  >
    <GMapMarker
      v-for="(m, index) in markers"
      :key="index"
      :position="m.position"
      :clickable="true"
      :icon="{
        url: 'src/assets/icons/pin.png',
        scaledSize: { width: 30, height: 30 },
        labelOrigin: { x: 16, y: -30 },
      }"
      @click="handleOpenMarker(m.id)"
    >
      <GMapInfoWindow
        :closeclick="true"
        :opened="openedMarkerID === m.id"
        class="px-8 py-8"
        @closeclick="handleOpenMarker(null)"
      >
        <ul>
          <li class="font-weight-bold">84.138.198.174</li>
          <li class="pb-8">p548ac6ae.dip0.t-ipconnect.de</li>
          <li>info</li>
          <li>info 2</li>
          <li>info 3</li>
        </ul>
      </GMapInfoWindow>
    </GMapMarker>
  </GMapMap>
</template>
<script setup lang="ts">
import { ref } from 'vue';

const center = ref({ lat: 51.093048, lng: 6.84212 });
// example
const markers = [
  {
    id: 1,
    position: {
      lat: 51.093048,
      lng: 6.84212,
    },
  },
  {
    id: 2,
    position: {
      lat: 51.198429,
      lng: 6.69529,
    },
  },
];
const openedMarkerID = ref();

function handleOpenMarker(id: number | null) {
  openedMarkerID.value = id;
}

const options = {
  // zoomControl: false,
  mapTypeControl: false,
  // scaleControl: true,
  streetViewControl: false,
  rotateControl: true,
  fullscreenControl: false,
  styles: [
    {
      featureType: 'all',
      elementType: 'geometry',
      stylers: [
        {
          color: '#202c3e',
        },
      ],
    },
    {
      featureType: 'all',
      elementType: 'labels.text.fill',
      stylers: [
        {
          gamma: 0.01,
        },
        {
          lightness: 20,
        },
        {
          weight: '1.39',
        },
        {
          color: '#ffffff',
        },
      ],
    },
    {
      featureType: 'all',
      elementType: 'labels.text.stroke',
      stylers: [
        {
          weight: '0.96',
        },
        {
          saturation: '9',
        },
        {
          visibility: 'on',
        },
        {
          color: '#000000',
        },
      ],
    },
    {
      featureType: 'all',
      elementType: 'labels.icon',
      stylers: [
        {
          visibility: 'off',
        },
      ],
    },
    {
      featureType: 'landscape',
      elementType: 'geometry',
      stylers: [
        {
          lightness: 30,
        },
        {
          saturation: '9',
        },
        {
          color: '#00a287',
        },
      ],
    },
    {
      featureType: 'poi',
      elementType: 'geometry',
      stylers: [
        {
          saturation: 20,
        },
      ],
    },
    {
      featureType: 'poi.park',
      elementType: 'all',
      stylers: [
        {
          saturation: '-16',
        },
        {
          lightness: '6',
        },
        {
          gamma: '1.00',
        },
        {
          color: '#00a287',
        },
      ],
    },
    {
      featureType: 'poi.park',
      elementType: 'geometry',
      stylers: [
        {
          lightness: 20,
        },
        {
          saturation: -20,
        },
        {
          visibility: 'simplified',
        },
      ],
    },
    {
      featureType: 'road',
      elementType: 'geometry',
      stylers: [
        {
          lightness: 10,
        },
        {
          saturation: -30,
        },
        {
          visibility: 'simplified',
        },
      ],
    },
    {
      featureType: 'road',
      elementType: 'geometry.fill',
      stylers: [
        {
          color: '#00846e',
        },
      ],
    },
    {
      featureType: 'road',
      elementType: 'geometry.stroke',
      stylers: [
        {
          saturation: 25,
        },
        {
          lightness: 25,
        },
        {
          weight: '0.01',
        },
      ],
    },
    {
      featureType: 'water',
      elementType: 'all',
      stylers: [
        {
          lightness: -20,
        },
        {
          color: '#041f20',
        },
      ],
    },
  ],
};
</script>
