(function(){
  var doc=document.documentElement;
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile menu
  var toggle=document.querySelector('.menu-toggle'),nav=document.getElementById('navigation');
  if(toggle&&nav){
    toggle.addEventListener('click',function(){
      var open=toggle.getAttribute('aria-expanded')!=='true';
      toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);
    });
    nav.addEventListener('click',function(e){if(e.target.tagName==='A'){toggle.setAttribute('aria-expanded','false');nav.classList.remove('open');}});
  }

  // Header shadow + sticky mobile CTA
  var header=document.querySelector('[data-header]'),sticky=document.querySelector('[data-sticky]'),hero=document.querySelector('.hero');
  function onScroll(){
    var y=window.scrollY;
    if(header)header.classList.toggle('scrolled',y>10);
    if(sticky&&hero)sticky.classList.toggle('show',y>hero.offsetHeight-120);
  }
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  // House grid: 100 squares, about 35 built before 1939, about 8 built 2000 or later
  var grid=document.querySelector('[data-grid]');
  if(grid){
    var html='';
    for(var i=0;i<100;i++){html+='<i class="'+(i<35?'old':(i>=92?'new':''))+'" style="transition-delay:'+(i*12)+'ms"></i>';}
    grid.innerHTML=html;
  }

  function countUp(el){
    var target=parseFloat(el.dataset.count),dec=+el.dataset.dec||0,suffix=el.dataset.suffix||'';
    var fmt=function(v){return v.toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec})+suffix;};
    if(reduce){el.textContent=fmt(target);return;}
    var t0=null,dur=1400;
    function step(t){
      if(!t0)t0=t;var p=Math.min((t-t0)/dur,1),e=1-Math.pow(1-p,3);
      el.textContent=fmt(target*e);if(p<1)requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  if(!('IntersectionObserver' in window)||reduce){
    doc.classList.add('no-js');
    document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in');});
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
  },{threshold:.15,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
})();
