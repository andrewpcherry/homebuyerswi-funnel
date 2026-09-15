(function(){
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Original root ?s= links continue into the matching assessment branch.
  if(new URLSearchParams(location.search).has('s')&&location.pathname==='/homebuyerswi-funnel/'){location.replace('get-a-cash-offer-today/'+location.search+'#quiz');return;}

  // Mobile menu
  var toggle=document.querySelector('.menu-toggle'),nav=document.getElementById('navigation');
  if(toggle&&nav){
    toggle.addEventListener('click',function(){var open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
  }

  // Header shadow and sticky mobile CTA
  var header=document.querySelector('[data-header]'),sticky=document.querySelector('[data-sticky]'),hero=document.querySelector('.hero,.page-hero');
  function onScroll(){
    var y=window.scrollY;
    if(header)header.classList.toggle('scrolled',y>10);
    if(sticky)sticky.classList.toggle('show',y>(hero?hero.offsetHeight-120:300));
  }
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  // Resource library search
  var search=document.getElementById('resource-search');
  if(search){
    search.addEventListener('input',function(){
      var q=search.value.trim().toLowerCase(),count=0;
      document.querySelectorAll('.library .resource-card').forEach(function(c){c.hidden=q&&!c.textContent.toLowerCase().includes(q);if(!c.hidden)count++;});
      document.getElementById('no-results').hidden=count>0;
    });
  }

  // House grid: 100 squares, about 35 built before 1939, about 8 built 2000 or later
  var grid=document.querySelector('[data-grid]');
  if(grid){var h='';for(var i=0;i<100;i++){h+='<i class="'+(i<35?'old':(i>=92?'new':''))+'" style="transition-delay:'+(i*12)+'ms"></i>';}grid.innerHTML=h;}

  function countUp(el){
    var target=parseFloat(el.dataset.count),dec=+el.dataset.dec||0,suffix=el.dataset.suffix||'';
    var fmt=function(v){return v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec})+suffix;};
    if(reduce){el.textContent=fmt(target);return;}
    var t0=null;
    function step(t){if(!t0)t0=t;var p=Math.min((t-t0)/1400,1);el.textContent=fmt(target*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(step);}
    requestAnimationFrame(step);
  }

  var items=document.querySelectorAll('.reveal');
  if(!('IntersectionObserver' in window)||reduce){
    document.documentElement.classList.add('no-js');
    items.forEach(function(el){el.classList.add('in');});
    if(grid)grid.classList.add('on');
    return;
  }
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(!en.isIntersecting)return;
      var el=en.target;el.classList.add('in');
      if(el.classList.contains('mke-copy'))el.querySelectorAll('[data-count]').forEach(countUp);
      if(el.classList.contains('mke-visual')&&grid)grid.classList.add('on');
      io.unobserve(el);
    });
  },{threshold:.12,rootMargin:'0px 0px -30px 0px'});
  items.forEach(function(el){io.observe(el);});
})();
