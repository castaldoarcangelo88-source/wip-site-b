document.querySelectorAll('figure.fb-post').forEach(function(f){
  var b=f.querySelector('.fb-post-carica'); if(!b) return;
  b.addEventListener('click',function(){
    var u=f.getAttribute('data-fb'); if(!/^https:\/\/www\.facebook\.com\//.test(u)) return;
    var i=document.createElement('iframe');
    i.src='https://www.facebook.com/plugins/post.php?href='+encodeURIComponent(u)+'&show_text=true&width=500';
    i.width='500'; i.height='620'; i.style.cssText='border:none;overflow:hidden;max-width:100%';
    i.setAttribute('scrolling','no'); i.setAttribute('loading','lazy'); i.setAttribute('allowfullscreen','true');
    i.setAttribute('allow','clipboard-write; encrypted-media; picture-in-picture; web-share');
    i.title='Post di HandiMap su Facebook';
    f.innerHTML=''; f.appendChild(i);
  });
});
