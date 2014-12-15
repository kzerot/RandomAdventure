var refreshTime = 25000;
var isUpdating = false;
var heroes = {};
var toIncrease = {};
var currentHero = {};
var currentParam = {};

function updateHeroes(data){
    for(var d in data['data']){
        var heroData = data['data'][d];
        var exp = heroData['exp'];
        $("#exp_"+heroData['id']).html(exp);
        console.log( $("#exp_"+heroData['id']), heroData, exp);
        heroes[heroData['id']] = heroData;
        for(var b in heroData['bars']){
            var bar = heroData['bars'][b];
            var b_id = 'bars_'+heroData['id']+"_"+bar.id;
            $('#'+b_id).html(bar.value);
            $('#'+b_id).css("width", Math.round(bar.value/bar.max*100)+'%');
            console.log(b_id);
             console.log( bar);
        }
        for(var b in heroData.params){
            var param = heroData.params[b];
            var b_id = 'param_'+heroData['id']+"_"+param.id;
            $('#'+b_id).html(param.value);
        }
    }
    isUpdating=false;
}

function updateAjax(){
    if(isUpdating)
        return;
    isUpdating = true;
   $.ajax({
      url: "/json",
      type: "POST",
      data: JSON.stringify({"action":'refresh'}),
      dataType: "json",
    })
  .done(function( data ) {
        updateHeroes(data);
    });
}

function changeData(el_id, delta){
    var el = $("#"+el_id);
    var current = parseInt(el.attr("value"));
    console.log(el);
    var data = el_id.split('_');
    var type = data[0];
    var hero = data[1];

    var atr = data[2];
     el.attr("value", current+delta);
    $.ajax({
      url: "/json",
      type: "POST",
      data: JSON.stringify({"action":'update', 'type': type, 'hero':hero, 'name': atr, 'delta':delta}),
      dataType: "json",
    })
    .done(function( data ) {
        console.log(data);
        updateHeroes(data);
    });

}

function expUp(el_id){
    $('#expUp').modal('show');
    toIncrease = {};
    var data = el_id.split('_');
    var type = data[0];
    var hero_id = data[1];
    var hero = heroes[hero_id];
    currentHero = hero;
    var exp_data = $('#exp_data');
    exp_data.html('');
    exp_data.html(add_div(add_p("Свободный опыт: ", "up_exp")+add_p(hero.exp, "up_exp", "up_exp")));
    for(var param_index in hero['params']){
        console.log( hero['params'][param_index]);
        var param = hero['params'][param_index];
        if(param.value){
            var html = add_div(add_p(param.name, 'up_param'), 'half_column');
            var tmp = add_p(param.value,  'up_param', 'modal_'+param.id);
            if( param.cost <= parseInt($('#up_exp').html()))
                tmp+=add_p('+',  'text_button_small up', 'modal-up_'+param.id);
            html +=  add_div(tmp, 'half_column', false, 'text-align:right');

            html = add_div(html, 'up_param')
            html += add_div("","clear");
            if(param['desc']){
                html += add_div(param.desc, 'desc');
            }

            html += add_div("Стоимость повышения характеристики: " + param.cost, 'desc');

            html += add_div("","divider_sm");
            exp_data.append(html);

        }
    }
    $('.up').click(function(){
    console.log($(this));
        var el_id = $(this).attr('id');
        var name  = el_id.split('_')[1];
        if(!toIncrease[name]){
            toIncrease[name] = 1;
        }else{
            toIncrease[name] += 1;
        }
        increaseVal(el_id.replace('modal-up', 'modal'));
        var param = {};
        for(var p in currentHero.params){
            if (currentHero.params[p].id == name){
                param = currentHero.params[p];
                break;
            }
        }

        changeVal('up_exp', -param.cost);
        checkUp();
    }
    );
}

function checkUp(){
    var els =  $('.up');
    els.each(function( index ) {
        var el_id = $( this ).attr('id');
        var name  = el_id.split('_')[1];
        var exp = parseInt($('#up_exp').html());
        var param = {};
        for(var p in currentHero.params){
            if (currentHero.params[p].id == name){
                param = currentHero.params[p];
                break;
            }
        }

        if(exp<param.cost)
            $('#'+el_id).remove();
    });
}


function changeVal(el_id, delta){
    $('#'+el_id).html(parseInt( $('#'+el_id).html())+delta);
}
function increaseVal(el_id){
    $('#'+el_id).html(parseInt( $('#'+el_id).html())+1);
}

function saveUp(){
     $.ajax({
          url: "/json",
          type: "POST",
          data: JSON.stringify({"action":'level_up', 'hero':currentHero.id, 'type':'params', 'data': toIncrease}),
          dataType: "json",
        })
        .done(function( data ) {
            console.log(data);
            updateHeroes(data);
        });
        $('#expUp').modal('hide')
}

$( document ).ready(function() {
    updateAjax();
    setInterval(updateAjax, refreshTime);
    $('.button_plus').click(function(data){
        changeData($(this).attr("value"), 1);
    });
    $('.button_minus').click(function(data){
        changeData($(this).attr("value"), -1);
    });
    $('.exp').click(function(data){
        expUp($(this).attr("value"));
    });
    $('#save_btn').click(function(data){
        saveUp();
    });

});


function add_some(text, el_class, el_id, style, type){
    var result = '<'+ type;
    if(el_id)
        result += ' id="' + el_id + '"';
    if(el_class)
        result += ' class="' + el_class + '"';
    if(style)
        result += ' style="' + style + '"';
    result += '>';
    result += text;
    result += '</' + type + '>';
    return result;
}
function add_p(text, el_class, el_id, style){
    return add_some(text, el_class, el_id, style, 'p');
}
function add_div(text, el_class, el_id, style){
    return add_some(text, el_class, el_id, style, 'div');
}