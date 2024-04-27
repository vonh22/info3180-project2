<script setup>
import { RouterLink } from "vue-router";
import { ref, onMounted, onUpdated } from "vue";
import router from "../router/index";

let info = ref(false);

let csrf_token = ref("");
let logged_in = ref("");
let current_user_id = ref("");


let getCsrfToken = async () => {
    const response = await fetch('/api/v1/csrf-token');
    return response.json();
};


let getUserId = async () => {
    const response = await fetch('/api/v1/loggedin');
    return response.json();
};

onMounted(async () => {
  let token = await getCsrfToken();
  csrf_token.value = token.csrf_token;

  let user_id = await getUserId();
  current_user_id.value = user_id.id;
  logged_in.value = user_id.logged_in
  
  info.value = true;
})

onUpdated(() => {
  const alert = document.querySelector("#alert");

  if(logged_in.value){
    const logoutBtn = document.querySelector("#logout-btn");
    logoutBtn.addEventListener('click', () => {
      router.push('/logout')
    })
  } else {
    const loginBtn = document.querySelector("#login-btn");
    loginBtn.addEventListener('click', () => {
      router.push('/login')
    })
  }
})
</script>

<template>
  <header v-if="info">
      <nav>
        <ul>
            <div class="logo">
              <li class="nav-item">
                <RouterLink class="nav-link" to="/"><span><i class="fa-solid fa-camera camera-icon"></i></span>Photogram</RouterLink>
              </li>
            </div>
            <div class="secondary-navs">
              <li class="nav-item">
                <RouterLink class="nav-link" to="/">Home</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" to="/explore">Explore</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="'/users/' + current_user_id">My Profile</RouterLink>
              </li>
              <li v-if="logged_in==true" class="nav-item">
                <RouterLink class="nav-link" to="/" id="logout-btn">Logout</RouterLink>
              </li>
              <li v-else class="nav-item">
                <RouterLink class="nav-link" to="/" id="login-btn">Login</RouterLink>
              </li>
            </div>
        </ul>
      </nav>
  </header>
  <div class="alert" id="alert"></div>
</template>
