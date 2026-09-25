const CACHE="one-thing-v1";


self.addEventListener(
"install",
event=>{

event.waitUntil(

caches.open(CACHE)

);

});


self.addEventListener(
"fetch",
event=>{

event.respondWith(

fetch(event.request)

);

});