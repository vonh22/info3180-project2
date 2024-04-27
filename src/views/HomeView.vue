<template>
<div class="alert" id="alert"></div>
  <div class="cards">
      <div class="photo-card photo-card-home">
          <img src="@/assets/display.jpg" alt="" class="home-img">
      </div>
      <div class="photo-card photo-card-text photo-card-home">
          <div class="logo"><p><span><i class="fa-solid fa-camera"></i></span>Photogram</p></div>
          <hr>
          <div class="photo-card-content">
              <p>Share photos of your favourite moments with friends, family and the world.</p>
              <div class="photo-card-btns">
                  <button class="btn btn-register"><RouterLink to="/register">Register</RouterLink></button>
                  <button class="btn btn-login"><RouterLink to="/login">Login</RouterLink></button>
              </div>
          </div>
      </div>
  </div>
</template>