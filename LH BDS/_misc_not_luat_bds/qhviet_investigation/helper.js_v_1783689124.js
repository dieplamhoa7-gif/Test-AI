const x0 = {};
const x00 = JSON;
x00.sgf = function(ob){return x00.stringify(ob);}
x00.x0 = function(ob, yb){return localStorage.setItem(ob, yb);}
x00.x00 = function(ob){return localStorage.getItem(ob);}
x00.x0x = function(ob){return localStorage.removeItem(ob);}
x0.x00 = function(ob){return btoa(ob)}
x0.xx0 = function(ob){return atob(ob);}
x0.x0 = function(ob){return x0.x00(x00.stringify(ob));}
x0.x0x = function(ob){return x00.parse(ob);}


window.getFeatureArea = function(geometry){
    if(typeof geodesic == 'undefined'){
        return 0;
    }

    var geod = geodesic.Geodesic.WGS84;

    function getLatLng(coor){
        if(typeof coor.lng != 'undefined' && typeof coor.lat != 'undefined'){
            return coor;
        }
        
        return coor[0] > coor[1] ? {
            lat: coor[1],
            lng: coor[0]
        } : {
            lat: coor[0],
            lng: coor[1]
        }
    }
    
    if(geometry.type == 'Polygon'){
        let area = 0;
        for (let index = 0; index < geometry.coordinates.length; index++) {
            const element = geometry.coordinates[index];
            var p = geod.Polygon(false);
            for (var i = 0; i < element.length; ++i){
                let point = getLatLng(element[i]);
                p.AddPoint(point.lat, point.lng);
            }
            p = p.Compute(true, true);

            area = index == 0 ? Math.abs(p.area) : area - Math.abs(p.area);
        }

        return Math.abs(area);
    }

    if(geometry.type == 'MultiPolygon'){
        let area = 0;
        for (let index = 0; index < geometry.coordinates.length; index++) {
            let polygonArea = window.getFeatureArea({
                type: 'Polygon',
                coordinates: geometry.coordinates[index]
            });

            area = area + polygonArea;
        }

        return area;
    }

    return 0;
}

window.removeVietnameseTones = function(str){
    let slug = str.toLowerCase();
    slug = slug.replace(/á|à|ả|ạ|ã|ă|ắ|ằ|ẳ|ẵ|ặ|â|ấ|ầ|ẩ|ẫ|ậ/gi, 'a');
    slug = slug.replace(/é|è|ẻ|ẽ|ẹ|ê|ế|ề|ể|ễ|ệ/gi, 'e');
    slug = slug.replace(/i|í|ì|ỉ|ĩ|ị/gi, 'i');
    slug = slug.replace(/ó|ò|ỏ|õ|ọ|ô|ố|ồ|ổ|ỗ|ộ|ơ|ớ|ờ|ở|ỡ|ợ/gi, 'o');
    slug = slug.replace(/ú|ù|ủ|ũ|ụ|ư|ứ|ừ|ử|ữ|ự/gi, 'u');
    slug = slug.replace(/ý|ỳ|ỷ|ỹ|ỵ/gi, 'y');
    slug = slug.replace(/đ/gi, 'd');
    slug = slug.replace(/\`|\~|\!|\@|\#|\||\$|\%|\^|\&|\*|\(|\)|\+|\=|\,|\.|\/|\?|\>|\<|\'|\"|\:|\;|_/gi, '');
    return slug;
}

window.replaceDistrictKeywords = function(str) {
    const map = {
        "quận ": "Q.",
        "huyện ": "H.",
        "phường ": "P.",
        "thành phố ": "TP.",
        "tỉnh ": "T."
    };

    const regex = new RegExp("\\b(" + Object.keys(map).join("|") + ")\\b", "gi");

    return str.replace(regex, (match) => {
        const lower = match.toLowerCase();
        let replacement = map[lower] || match;

        // Nếu từ gốc viết hoa chữ cái đầu thì cũng viết hoa kết quả
        if (match[0] === match[0].toUpperCase()) {
            replacement = replacement[0].toUpperCase() + replacement.slice(1);
        }
        return replacement;
    });
}

window.removeFirstPart = function(str) {
    const parts = str.split("-").map(s => s.trim());
    parts.shift();
    return parts.join(" - ");
}

window.uniqueFeatures = function(features) {
    let seen = new Set();
    let unique = [];

    features.forEach(f => {
        let key = JSON.stringify(f.geometry);
        if (!seen.has(key)) {
            seen.add(key);
            unique.push(f);
        }
    });

    return unique;
}

window.geobufEncode = function(feature){
    let buffer = geobuf.encode(feature, new Pbf());
    let pbfString = btoa(buffer.reduce((s, byte) => s + String.fromCharCode(byte), ""));
    return pbfString;
}

window.dataURLToBlob = function(dataURL) {
    var BASE64_MARKER = ';base64,';
    if (dataURL.indexOf(BASE64_MARKER) == -1) {
        var parts = dataURL.split(',');
        var contentType = parts[0].split(':')[1];
        var raw = parts[1];

        return new Blob([raw], {type: contentType});
    }

    var parts = dataURL.split(BASE64_MARKER);
    var contentType = parts[0].split(':')[1];
    var raw = window.atob(parts[1]);
    var rawLength = raw.length;

    var uInt8Array = new Uint8Array(rawLength);

    for (var i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }

    return new Blob([uInt8Array], {type: contentType});
}

window.blobToBase64 = function(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            resolve(reader.result); // đây là chuỗi base64
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    })
}

window.blobToBase64 = function(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            resolve(reader.result); // đây là chuỗi base64
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    })
}

window.base64ToFile = function(base64String, fileName) {
    const arr = base64String.split(',');
    const mimeMatch = arr[0].match(/:(.*?);/);
    const mime = mimeMatch ? mimeMatch[1] : '';
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);

    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }

    return new File([u8arr], fileName, { type: mime });
}

window.resizeImage = function(file){
    return new Promise(async (resolve, reject)=>{
        if(typeof file == 'string'){
            // fetch từ objectURL để lấy Blob
            const response = await fetch(file);
            file = await response.blob();
        }

        if(file.type.match(/image.*/)) {
            var reader = new FileReader();
            reader.onload = function (readerEvent) {
                var image = new Image();
                image.onload = function (imageEvent) {

                    // Resize the image
                    var canvas = document.createElement('canvas'),
                        max_size = 1200,
                        width = image.width,
                        height = image.height;
                    if (width > height) {
                        if (width > max_size) {
                            height *= max_size / width;
                            width = max_size;
                        }
                    } else {
                        if (height > max_size) {
                            width *= max_size / height;
                            height = max_size;
                        }
                    }
                    canvas.width = width;
                    canvas.height = height;
                    canvas.getContext('2d').drawImage(image, 0, 0, width, height);
                    var dataUrl = canvas.toDataURL('image/jpeg');
                    var resizedImage = window.dataURLToBlob(dataUrl);
                    resolve(resizedImage);
                }
                image.src = readerEvent.target.result;
            }
            reader.readAsDataURL(file);
        }else{
            reject();
        }
    })
}