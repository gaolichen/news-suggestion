// ==UserScript==
// @name         News Suggestion
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       Gaoli Chen
// @match        https://www.backchina.com/*
// @match        https://www.dwnews.com/*
// @match        https://blog.dwnews.com/*
// @match        https://*.sina.com.cn/*
// @grant        none
// ==/UserScript==

var url2Save = 'http://localhost:5000/savenews';

class NewsSite {
    constructor(domain) {
        this.domain = domain;
        this.titleSelector = 'h1';
    }

    isIndexUrl(url) {
        return url.includes(this.domain);
    }

    isNewsUrl(url) {
        return url.includes(this.domain);
    }

    queryNewsLinks(onFound) {
    }

    getNews() {
        let ret = [];
        this.queryNewsLinks((url, textElem) => {
            url = getUrlWithoutQuery(url);
            if (this.isNewsUrl(url) && textElem.innerText) {
                ret.push(newsInfo(url, textElem.innerText));
            }
        });

        return ret;
    }

    highlight(urlsToHightlight) {
        let urls = [];
        for (let i = 0; i < urlsToHightlight.length && i < 10; i++) {
            console.log('highlighting ' + urlsToHightlight[i].href + ' ' + urlsToHightlight[i].score);
            urls.push(urlsToHightlight[i].href);
        }

        this.queryNewsLinks((url, textElem) => {
            url = getUrlWithoutQuery(url);
            if (urls.includes(url)) {
                textElem.style.backgroundColor = 'yellow';
            }
        });
    }

    getTitle() {
        let elem = document.querySelectorAll(this.titleSelector);
        if (elem && elem.length) {
            return elem[0].innerText;
        } else {
            console.log('cannot find title with selector' + this.titleSelector);
            return '';
        }
    }
}

let sinaSections = ['要闻', '体育', '娱乐', '科技', '财经'];
class SinaNews extends NewsSite {
    constructor() {
        super('sina.com');
        this.titleSelector = 'h1.main-title';
    }

    isIndexUrl(url) {
        return url == 'https://www.sina.com.cn/'
    }

    isNewsUrl(url) {
        console.log('isNewsUrl=' + url);
        return super.isNewsUrl(url) && (url.endsWith('html') || url.endsWith('shtml')) &&
            !url.includes('slide') && !url.includes('/comment');
    }

    queryNewsLinks(onFound) {
        for (let i = 0; i < sinaSections.length; i++) {
            let elem = document.querySelectorAll('div[blktitle=' + sinaSections[i] + ']');
            if (!elem) {
                continue;
            }
            let links = null;
            // need special handing as there are hidden elements should not be retrieved.
            if (sinaSections[i] == '要闻') {
                links = document.getElementById('newslist_a').querySelectorAll('ul > li > a');
            } else {
                links = elem[0].querySelectorAll('ul > li > a');
            }
            console.log(sinaSections[i] + " " + links.length);
            for (let j = 0; j < links.length; j++) {
                onFound(links[j].href, links[j]);
            }
        }
    }
}

class BackchinaNews extends NewsSite {
    constructor() {
        super('backchina.com');
        this.titleSelector = 'h1.ph';
    }

    isIndexUrl(url) {
        return url == 'https://www.backchina.com/'
    }

    isNewsUrl(url) {
        return super.isNewsUrl(url) && url.endsWith('html') && (url.includes('/news/') || url.includes('/blog/')) && !url.includes('/comment');
    }

    queryNewsLinks(onFound) {
        var elem = document.querySelectorAll('ul.eis_toplist > li > a');
        for (let i = 0; i < elem.length; i++) {
            onFound(elem[i].href, elem[i]);
        }
    }
}

class DWNews extends NewsSite {
    constructor() {
        super('dwnews.com');
        this.titleSelector = 'h1';
    }

    isIndexUrl(url) {
        return url == 'https://www.dwnews.com/'
    }

    isNewsUrl(url) {
        if (!super.isNewsUrl(url)) {
            return false;
        }

        if (url.includes('/视觉/')) {
            return false;
        }

        if (url.includes('blog.dwnews.com') && url.endsWith('.html')) {
            return true;
        }

        let parts = url.split('/');
        if (parts.length < 5) {
            return false;
        }
        return toInt(parts[parts.length - 2], 0) > 0;
    }

    queryNewsLinks(onFound) {
        var elem = document.querySelectorAll('a[data-testid] > div');
        for (let i = 0; i < elem.length; i++) {
            let url = decodeURI(elem[i].parentNode.href);
            onFound(url, elem[i]);
            //console.log(elem[i].innerText + " " + decodeURI(elem[i].parentNode.href));
        }
    }
}

var newsSites = [new SinaNews(), new BackchinaNews(), new DWNews()]

async function putData(newsList, site, ignoreIfExists) {
    let myHeaders = new Headers();
    myHeaders.append('Content-Type', 'application/json');
    let obj1 = {"content":newsList, "ignore_if_exists": ignoreIfExists, "site": site};
    console.log("ignore_if_exists=" + ignoreIfExists);
    const myInit = {
        method: 'PUT',
        headers: myHeaders,
        body: JSON.stringify(obj1)
    };
    let response = await fetch(url2Save, myInit);
    if (response.status == 200) {
        return await response.json();
    } else {
        throw Error(response.status);
    }
}

function newsInfo(url, title, read = false) {
    if (read) {
        return {'href' : url, 'title' : title, 'last_visited' : Date.now(), 'created' : Date.now()};
    } else {
        return {'href' : url, 'title' : title, 'last_visited' : 0, 'created' : Date.now()};
    }
}

function getUrlWithoutQuery(url) {
    let pos = url.indexOf('?');
    if (pos >= 0) {
        return url.substring(0, pos);
    } else {
        return url;
    }
}

function markVisited(url, title, site) {
    console.log("page visited: " + url + " " + title);
    sendNewsListToSever([newsInfo(url, title, true)], site, false)
    .catch(err => console.log(err));
}

function toInt(str, defaultValue) {
    let ret = parseInt(str);
    if (Number.isNaN(ret)) {
        return defaultValue;
    } else {
        return ret;
    }
}

function getNewsListFromLocalStorage() {
    let storage = window.localStorage;
    const ret = new Set()
    let count = toInt(storage.getItem("news_count"), 0);
    for (let i = 0; i < count; i++) {
        ret.add(storage.getItem("news_url_" + i));
    }

    return ret
}

function saveNewsListToLocalStorage(newsList) {
    let storage = window.localStorage;
    let count = toInt(storage.getItem("news_count"), 0);
    for (let i = 0; i < newsList.length; i++) {
        storage.setItem("news_url_" + i, newsList[i].href);
    }
    for (let i = newsList.length; i < count; i++) {
        storage.removeItem("news_url_" + i);
    }

    storage.setItem("news_count", newsList.length);
}

async function sendNewsListToSever(newsList, site, fromNewsPage = true) {
    console.log('sending to server..');
    for (let i = 0; i < newsList.length; i++) {
        console.log(i + " " + newsList[i].title + newsList[i].href);
    }
    console.log('sendNewsListToSever fromNewsPage=' + fromNewsPage);
    let flag = fromNewsPage ? 1 : 0;
    return await putData(newsList, site, flag);
}

function newsRetrieved(newsList, site, onhighlight) {
    console.log("no. of news = " + newsList.length);
    // unique the list
    const newsMap = new Map()
    for (let i = 0; i < newsList.length; i++) {
        if (!newsMap.has(newsList[i].href)) {
            newsMap.set(newsList[i].href, newsList[i].title);
        }
    }

    let uniqueList = [];
    for (const [key, value] of newsMap) {
        uniqueList.push(newsInfo(key, value, false));
    }

    let cache = getNewsListFromLocalStorage();
    let listToSend = [];

    for (let i = 0; i < uniqueList.length; i++) {
        if (cache.has(uniqueList[i].href)) {
            continue;
        }
        listToSend.push(uniqueList[i]);
    }
    sendNewsListToSever(listToSend, site, true)
    .then(unvisited => {
        console.log('Succeed sending news list to server.');
        saveNewsListToLocalStorage(uniqueList);
        onhighlight(unvisited);
    })
    .catch(err => console.log('Failed sending news list with error: ' + err));
}

function clearData() {
    saveNewsListToLocalStorage([]);
}

function process() {
    let url = decodeURI(window.location.href);
    url = getUrlWithoutQuery(url);
    console.log('page url=' + url);

    for (let i = 0; i < newsSites.length; i++) {
        if (newsSites[i].isIndexUrl(url)) {
            let news = newsSites[i].getNews();
            newsRetrieved(news, newsSites[i].domain, (urls) => newsSites[i].highlight(urls));
            break;
        } else if (newsSites[i].isNewsUrl(url) && newsSites[i].getTitle()) {
            markVisited(url, newsSites[i].getTitle(), newsSites[i].domain);
            break;
        }
    }
}

(function() {
//window.addEventListener('load', function() {
    'use strict';
    //clearData();
    setTimeout(() => process(), 2000);
//}, false);
})();