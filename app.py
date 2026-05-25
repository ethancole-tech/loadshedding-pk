from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import hashlib
import pytz
import re
import os
import random

load_dotenv()
app = Flask(__name__)
PKT = pytz.timezone('Asia/Karachi')

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def now_pkt():
    return datetime.now(PKT)

# ══════════════════════════════════════════════════════════════════════════════
#  AREAS — 400+ hardcoded across all 8 DISCOs
# ══════════════════════════════════════════════════════════════════════════════
AREAS = {

    # ── LESCO — Lahore Division ──────────────────────────────────────────────
    'gulberg':                  {'disco': 'LESCO', 'city': 'Lahore'},
    'johar town':               {'disco': 'LESCO', 'city': 'Lahore'},
    'model town':               {'disco': 'LESCO', 'city': 'Lahore'},
    'dha lahore':               {'disco': 'LESCO', 'city': 'Lahore'},
    'iqbal town':               {'disco': 'LESCO', 'city': 'Lahore'},
    'garden town':              {'disco': 'LESCO', 'city': 'Lahore'},
    'wapda town':               {'disco': 'LESCO', 'city': 'Lahore'},
    'township':                 {'disco': 'LESCO', 'city': 'Lahore'},
    'samanabad':                {'disco': 'LESCO', 'city': 'Lahore'},
    'allama iqbal town':        {'disco': 'LESCO', 'city': 'Lahore'},
    'raiwind':                  {'disco': 'LESCO', 'city': 'Lahore'},
    'shahdara':                 {'disco': 'LESCO', 'city': 'Lahore'},
    'kot lakhpat':              {'disco': 'LESCO', 'city': 'Lahore'},
    'cantt lahore':             {'disco': 'LESCO', 'city': 'Lahore'},
    'faisal town':              {'disco': 'LESCO', 'city': 'Lahore'},
    'shaukat town':             {'disco': 'LESCO', 'city': 'Lahore'},
    'walton':                   {'disco': 'LESCO', 'city': 'Lahore'},
    'mughal pura':              {'disco': 'LESCO', 'city': 'Lahore'},
    'data gunj bakhsh':         {'disco': 'LESCO', 'city': 'Lahore'},
    'baghbanpura':              {'disco': 'LESCO', 'city': 'Lahore'},
    'green town':               {'disco': 'LESCO', 'city': 'Lahore'},
    'cavalry ground':           {'disco': 'LESCO', 'city': 'Lahore'},
    'bahria town lahore':       {'disco': 'LESCO', 'city': 'Lahore'},
    'dha phase 1':              {'disco': 'LESCO', 'city': 'Lahore'},
    'dha phase 2':              {'disco': 'LESCO', 'city': 'Lahore'},
    'dha phase 3':              {'disco': 'LESCO', 'city': 'Lahore'},
    'dha phase 4':              {'disco': 'LESCO', 'city': 'Lahore'},
    'dha phase 5':              {'disco': 'LESCO', 'city': 'Lahore'},
    'dha phase 6':              {'disco': 'LESCO', 'city': 'Lahore'},
    'lahore':                   {'disco': 'LESCO', 'city': 'Lahore'},
    'shalimar':                 {'disco': 'LESCO', 'city': 'Lahore'},
    'ichra':                    {'disco': 'LESCO', 'city': 'Lahore'},
    'garhi shahu':              {'disco': 'LESCO', 'city': 'Lahore'},
    'gulshan ravi':             {'disco': 'LESCO', 'city': 'Lahore'},
    'anarkali':                 {'disco': 'LESCO', 'city': 'Lahore'},
    'liberty market':           {'disco': 'LESCO', 'city': 'Lahore'},
    'defence lahore':           {'disco': 'LESCO', 'city': 'Lahore'},
    'thokar niaz baig':         {'disco': 'LESCO', 'city': 'Lahore'},
    'manga mandi':              {'disco': 'LESCO', 'city': 'Lahore'},
    'kahna':                    {'disco': 'LESCO', 'city': 'Lahore'},
    'sundar':                   {'disco': 'LESCO', 'city': 'Lahore'},
    'ferozwala':                {'disco': 'LESCO', 'city': 'Sheikhupura'},
    'sheikhupura':              {'disco': 'LESCO', 'city': 'Sheikhupura'},
    'muridke':                  {'disco': 'LESCO', 'city': 'Sheikhupura'},
    'safdarabad':               {'disco': 'LESCO', 'city': 'Sheikhupura'},
    'nankana sahib':            {'disco': 'LESCO', 'city': 'Nankana Sahib'},
    'sangla hill':              {'disco': 'LESCO', 'city': 'Nankana Sahib'},
    'chunian':                  {'disco': 'LESCO', 'city': 'Kasur'},
    'kasur':                    {'disco': 'LESCO', 'city': 'Kasur'},
    'kot radha kishan':         {'disco': 'LESCO', 'city': 'Kasur'},
    'pattoki':                  {'disco': 'LESCO', 'city': 'Kasur'},

    # ── GEPCO — Gujranwala Division ──────────────────────────────────────────
    'gujranwala':               {'disco': 'GEPCO', 'city': 'Gujranwala'},
    'sialkot':                  {'disco': 'GEPCO', 'city': 'Sialkot'},
    'gujrat':                   {'disco': 'GEPCO', 'city': 'Gujrat'},
    'hafizabad':                {'disco': 'GEPCO', 'city': 'Hafizabad'},
    'wazirabad':                {'disco': 'GEPCO', 'city': 'Wazirabad'},
    'narowal':                  {'disco': 'GEPCO', 'city': 'Narowal'},
    'pasrur':                   {'disco': 'GEPCO', 'city': 'Sialkot'},
    'daska':                    {'disco': 'GEPCO', 'city': 'Sialkot'},
    'sambrial':                 {'disco': 'GEPCO', 'city': 'Sialkot'},
    'kamoke':                   {'disco': 'GEPCO', 'city': 'Gujranwala'},
    'kharian':                  {'disco': 'GEPCO', 'city': 'Gujrat'},
    'phalia':                   {'disco': 'GEPCO', 'city': 'Gujrat'},
    'shakargarh':               {'disco': 'GEPCO', 'city': 'Narowal'},
    'zafarwal':                 {'disco': 'GEPCO', 'city': 'Narowal'},
    'nowshera virkan':          {'disco': 'GEPCO', 'city': 'Gujranwala'},
    'alipur chatha':            {'disco': 'GEPCO', 'city': 'Gujranwala'},
    'qila didar singh':         {'disco': 'GEPCO', 'city': 'Gujranwala'},
    'aroop':                    {'disco': 'GEPCO', 'city': 'Hafizabad'},
    'pindi bhattian':           {'disco': 'GEPCO', 'city': 'Hafizabad'},

    # ── FESCO — Faisalabad Division ──────────────────────────────────────────
    'faisalabad':               {'disco': 'FESCO', 'city': 'Faisalabad'},
    'peoples colony':           {'disco': 'FESCO', 'city': 'Faisalabad'},
    'gulshan colony':           {'disco': 'FESCO', 'city': 'Faisalabad'},
    'madina town':              {'disco': 'FESCO', 'city': 'Faisalabad'},
    'jail road faisalabad':     {'disco': 'FESCO', 'city': 'Faisalabad'},
    'sargodha':                 {'disco': 'FESCO', 'city': 'Sargodha'},
    'jhang':                    {'disco': 'FESCO', 'city': 'Jhang'},
    'chiniot':                  {'disco': 'FESCO', 'city': 'Chiniot'},
    'toba tek singh':           {'disco': 'FESCO', 'city': 'Toba Tek Singh'},
    'bhakkar':                  {'disco': 'FESCO', 'city': 'Bhakkar'},
    'mianwali':                 {'disco': 'FESCO', 'city': 'Mianwali'},
    'susan road':               {'disco': 'FESCO', 'city': 'Faisalabad'},
    'satiana road':             {'disco': 'FESCO', 'city': 'Faisalabad'},
    'millat road':              {'disco': 'FESCO', 'city': 'Faisalabad'},
    'dijkot':                   {'disco': 'FESCO', 'city': 'Faisalabad'},
    'sammundri':                {'disco': 'FESCO', 'city': 'Faisalabad'},
    'chak jhumra':              {'disco': 'FESCO', 'city': 'Faisalabad'},
    'tandlianwala':             {'disco': 'FESCO', 'city': 'Faisalabad'},
    'jaranwala':                {'disco': 'FESCO', 'city': 'Faisalabad'},
    'shahkot':                  {'disco': 'FESCO', 'city': 'Faisalabad'},
    'gojra':                    {'disco': 'FESCO', 'city': 'Toba Tek Singh'},
    'kamalia':                  {'disco': 'FESCO', 'city': 'Toba Tek Singh'},
    'pirmahal':                 {'disco': 'FESCO', 'city': 'Toba Tek Singh'},
    'lalian':                   {'disco': 'FESCO', 'city': 'Chiniot'},
    'bhawana':                  {'disco': 'FESCO', 'city': 'Chiniot'},
    'kot momin':                {'disco': 'FESCO', 'city': 'Sargodha'},
    'bhalwal':                  {'disco': 'FESCO', 'city': 'Sargodha'},
    'sillanwali':               {'disco': 'FESCO', 'city': 'Sargodha'},
    'khushab':                  {'disco': 'FESCO', 'city': 'Khushab'},
    'joharabad':                {'disco': 'FESCO', 'city': 'Khushab'},
    'kalurkot':                 {'disco': 'FESCO', 'city': 'Bhakkar'},
    'mankera':                  {'disco': 'FESCO', 'city': 'Bhakkar'},
    'piplan':                   {'disco': 'FESCO', 'city': 'Mianwali'},
    'esa khel':                 {'disco': 'FESCO', 'city': 'Mianwali'},
    'wan bhachran':             {'disco': 'FESCO', 'city': 'Mianwali'},

    # ── MEPCO — Multan / South Punjab ────────────────────────────────────────
    'multan':                   {'disco': 'MEPCO', 'city': 'Multan'},
    'gulgasht':                 {'disco': 'MEPCO', 'city': 'Multan'},
    'cantt multan':             {'disco': 'MEPCO', 'city': 'Multan'},
    'bahauddin':                {'disco': 'MEPCO', 'city': 'Multan'},
    'bahawalpur':               {'disco': 'MEPCO', 'city': 'Bahawalpur'},
    'bahawalnagar':             {'disco': 'MEPCO', 'city': 'Bahawalnagar'},
    'rahim yar khan':           {'disco': 'MEPCO', 'city': 'Rahim Yar Khan'},
    'sahiwal':                  {'disco': 'MEPCO', 'city': 'Sahiwal'},
    'okara':                    {'disco': 'MEPCO', 'city': 'Okara'},
    'pakpattan':                {'disco': 'MEPCO', 'city': 'Pakpattan'},
    'khanewal':                 {'disco': 'MEPCO', 'city': 'Khanewal'},
    'lodhran':                  {'disco': 'MEPCO', 'city': 'Lodhran'},
    'vehari':                   {'disco': 'MEPCO', 'city': 'Vehari'},
    'muzaffargarh':             {'disco': 'MEPCO', 'city': 'Muzaffargarh'},
    'layyah':                   {'disco': 'MEPCO', 'city': 'Layyah'},
    'dera ghazi khan':          {'disco': 'MEPCO', 'city': 'Dera Ghazi Khan'},
    'dgk':                      {'disco': 'MEPCO', 'city': 'Dera Ghazi Khan'},
    'shujabad':                 {'disco': 'MEPCO', 'city': 'Multan'},
    'jalalpur pirwala':         {'disco': 'MEPCO', 'city': 'Multan'},
    'mian channu':              {'disco': 'MEPCO', 'city': 'Khanewal'},
    'kabirwala':                {'disco': 'MEPCO', 'city': 'Khanewal'},
    'burewala':                 {'disco': 'MEPCO', 'city': 'Vehari'},
    'mailsi':                   {'disco': 'MEPCO', 'city': 'Vehari'},
    'dunyapur':                 {'disco': 'MEPCO', 'city': 'Lodhran'},
    'kahror pacca':             {'disco': 'MEPCO', 'city': 'Lodhran'},
    'hasilpur':                 {'disco': 'MEPCO', 'city': 'Bahawalpur'},
    'ahmadpur east':            {'disco': 'MEPCO', 'city': 'Bahawalpur'},
    'uch sharif':               {'disco': 'MEPCO', 'city': 'Bahawalpur'},
    'yazman':                   {'disco': 'MEPCO', 'city': 'Bahawalpur'},
    'fort abbas':               {'disco': 'MEPCO', 'city': 'Bahawalnagar'},
    'haroonabad':               {'disco': 'MEPCO', 'city': 'Bahawalnagar'},
    'chishtian':                {'disco': 'MEPCO', 'city': 'Bahawalnagar'},
    'sadiqabad':                {'disco': 'MEPCO', 'city': 'Rahim Yar Khan'},
    'khanpur':                  {'disco': 'MEPCO', 'city': 'Rahim Yar Khan'},
    'liaquatpur':               {'disco': 'MEPCO', 'city': 'Rahim Yar Khan'},
    'chowk azam':               {'disco': 'MEPCO', 'city': 'Layyah'},
    'karor lal esan':           {'disco': 'MEPCO', 'city': 'Layyah'},
    'taunsa':                   {'disco': 'MEPCO', 'city': 'Dera Ghazi Khan'},
    'rajanpur':                 {'disco': 'MEPCO', 'city': 'Rajanpur'},
    'jampur':                   {'disco': 'MEPCO', 'city': 'Rajanpur'},
    'rojhan':                   {'disco': 'MEPCO', 'city': 'Rajanpur'},
    'arifwala':                 {'disco': 'MEPCO', 'city': 'Pakpattan'},
    'renala khurd':             {'disco': 'MEPCO', 'city': 'Okara'},
    'depalpur':                 {'disco': 'MEPCO', 'city': 'Okara'},

    # ── IESCO — Islamabad / Rawalpindi Division ───────────────────────────────
    'f-7':                      {'disco': 'IESCO', 'city': 'Islamabad'},
    'f-8':                      {'disco': 'IESCO', 'city': 'Islamabad'},
    'f-10':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'f-11':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'g-9':                      {'disco': 'IESCO', 'city': 'Islamabad'},
    'g-10':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'g-11':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'g-13':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'g-15':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'i-8':                      {'disco': 'IESCO', 'city': 'Islamabad'},
    'i-10':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'e-7':                      {'disco': 'IESCO', 'city': 'Islamabad'},
    'd-12':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'e-11':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'b-17':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'h-13':                     {'disco': 'IESCO', 'city': 'Islamabad'},
    'bahria town islamabad':    {'disco': 'IESCO', 'city': 'Islamabad'},
    'dha islamabad':            {'disco': 'IESCO', 'city': 'Islamabad'},
    'pwd':                      {'disco': 'IESCO', 'city': 'Islamabad'},
    'islamabad':                {'disco': 'IESCO', 'city': 'Islamabad'},
    'gulberg islamabad':        {'disco': 'IESCO', 'city': 'Islamabad'},
    'rawalpindi':               {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'satellite town':           {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'chaklala':                 {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'cantt rawalpindi':         {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'bahria town rwp':          {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'saddar rawalpindi':        {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'media town':               {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'morgah':                   {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'adyala':                   {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'taxila':                   {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'wah cantt':                {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'gujar khan':               {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'murree':                   {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'kahuta':                   {'disco': 'IESCO', 'city': 'Rawalpindi'},
    'chakwal':                  {'disco': 'IESCO', 'city': 'Chakwal'},
    'talagang':                 {'disco': 'IESCO', 'city': 'Chakwal'},
    'choa saidan shah':         {'disco': 'IESCO', 'city': 'Chakwal'},
    'attock':                   {'disco': 'IESCO', 'city': 'Attock'},
    'fateh jang':               {'disco': 'IESCO', 'city': 'Attock'},
    'hazro':                    {'disco': 'IESCO', 'city': 'Attock'},
    'hasan abdal':              {'disco': 'IESCO', 'city': 'Attock'},
    'pindi gheb':               {'disco': 'IESCO', 'city': 'Attock'},
    'jhelum':                   {'disco': 'IESCO', 'city': 'Jhelum'},
    'sohawa':                   {'disco': 'IESCO', 'city': 'Jhelum'},
    'dina':                     {'disco': 'IESCO', 'city': 'Jhelum'},

    # ── PESCO — KPK ──────────────────────────────────────────────────────────
    'peshawar':                 {'disco': 'PESCO', 'city': 'Peshawar'},
    'hayatabad':                {'disco': 'PESCO', 'city': 'Peshawar'},
    'cantt peshawar':           {'disco': 'PESCO', 'city': 'Peshawar'},
    'university town':          {'disco': 'PESCO', 'city': 'Peshawar'},
    'warsak road':              {'disco': 'PESCO', 'city': 'Peshawar'},
    'dalazak road':             {'disco': 'PESCO', 'city': 'Peshawar'},
    'badaber':                  {'disco': 'PESCO', 'city': 'Peshawar'},
    'mattani':                  {'disco': 'PESCO', 'city': 'Peshawar'},
    'abbottabad':               {'disco': 'PESCO', 'city': 'Abbottabad'},
    'havelian':                 {'disco': 'PESCO', 'city': 'Abbottabad'},
    'ayubia':                   {'disco': 'PESCO', 'city': 'Abbottabad'},
    'mansehra':                 {'disco': 'PESCO', 'city': 'Mansehra'},
    'naran':                    {'disco': 'PESCO', 'city': 'Mansehra'},
    'balakot':                  {'disco': 'PESCO', 'city': 'Mansehra'},
    'shinkiari':                {'disco': 'PESCO', 'city': 'Mansehra'},
    'mardan':                   {'disco': 'PESCO', 'city': 'Mardan'},
    'takht bhai':               {'disco': 'PESCO', 'city': 'Mardan'},
    'rustam':                   {'disco': 'PESCO', 'city': 'Mardan'},
    'swat':                     {'disco': 'PESCO', 'city': 'Swat'},
    'mingora':                  {'disco': 'PESCO', 'city': 'Swat'},
    'madyan':                   {'disco': 'PESCO', 'city': 'Swat'},
    'matta':                    {'disco': 'PESCO', 'city': 'Swat'},
    'bahrain':                  {'disco': 'PESCO', 'city': 'Swat'},
    'kohat':                    {'disco': 'PESCO', 'city': 'Kohat'},
    'lachi':                    {'disco': 'PESCO', 'city': 'Kohat'},
    'darra adam khel':          {'disco': 'PESCO', 'city': 'Kohat'},
    'nowshera':                 {'disco': 'PESCO', 'city': 'Nowshera'},
    'risalpur':                 {'disco': 'PESCO', 'city': 'Nowshera'},
    'pabbi':                    {'disco': 'PESCO', 'city': 'Nowshera'},
    'akora khattak':            {'disco': 'PESCO', 'city': 'Nowshera'},
    'charsadda':                {'disco': 'PESCO', 'city': 'Charsadda'},
    'haripur':                  {'disco': 'PESCO', 'city': 'Haripur'},
    'swabi':                    {'disco': 'PESCO', 'city': 'Swabi'},
    'topi':                     {'disco': 'PESCO', 'city': 'Swabi'},
    'razzar':                   {'disco': 'PESCO', 'city': 'Swabi'},
    'bannu':                    {'disco': 'PESCO', 'city': 'Bannu'},
    'dera ismail khan':         {'disco': 'PESCO', 'city': 'Dera Ismail Khan'},
    'dik':                      {'disco': 'PESCO', 'city': 'Dera Ismail Khan'},
    'tank':                     {'disco': 'PESCO', 'city': 'Tank'},
    'hangu':                    {'disco': 'PESCO', 'city': 'Hangu'},
    'karak':                    {'disco': 'PESCO', 'city': 'Karak'},
    'lakki marwat':             {'disco': 'PESCO', 'city': 'Lakki Marwat'},
    'chakdara':                 {'disco': 'PESCO', 'city': 'Dir Lower'},
    'timergara':                {'disco': 'PESCO', 'city': 'Dir Lower'},
    'dir':                      {'disco': 'PESCO', 'city': 'Dir Upper'},
    'chitral':                  {'disco': 'PESCO', 'city': 'Chitral'},
    'buner':                    {'disco': 'PESCO', 'city': 'Buner'},
    'daggar':                   {'disco': 'PESCO', 'city': 'Buner'},
    'shangla':                  {'disco': 'PESCO', 'city': 'Shangla'},
    'alpuri':                   {'disco': 'PESCO', 'city': 'Shangla'},
    'kohistan':                 {'disco': 'PESCO', 'city': 'Kohistan'},

    # ── HESCO — Hyderabad / Interior Sindh ───────────────────────────────────
    'hyderabad':                {'disco': 'HESCO', 'city': 'Hyderabad'},
    'latifabad':                {'disco': 'HESCO', 'city': 'Hyderabad'},
    'qasimabad':                {'disco': 'HESCO', 'city': 'Hyderabad'},
    'tando muhammad khan':      {'disco': 'HESCO', 'city': 'Hyderabad'},
    'matiari':                  {'disco': 'HESCO', 'city': 'Hyderabad'},
    'hala':                     {'disco': 'HESCO', 'city': 'Hyderabad'},
    'sukkur':                   {'disco': 'HESCO', 'city': 'Sukkur'},
    'rohri':                    {'disco': 'HESCO', 'city': 'Sukkur'},
    'pano aqil':                {'disco': 'HESCO', 'city': 'Sukkur'},
    'larkana':                  {'disco': 'HESCO', 'city': 'Larkana'},
    'nawabshah':                {'disco': 'HESCO', 'city': 'Nawabshah'},
    'mirpur khas':              {'disco': 'HESCO', 'city': 'Mirpur Khas'},
    'mirpur bathoro':           {'disco': 'HESCO', 'city': 'Mirpur Khas'},
    'umerkot':                  {'disco': 'HESCO', 'city': 'Mirpur Khas'},
    'sanghar':                  {'disco': 'HESCO', 'city': 'Sanghar'},
    'tando adam':               {'disco': 'HESCO', 'city': 'Sanghar'},
    'shahdadpur':               {'disco': 'HESCO', 'city': 'Sanghar'},
    'tando allahyar':           {'disco': 'HESCO', 'city': 'Tando Allahyar'},
    'badin':                    {'disco': 'HESCO', 'city': 'Badin'},
    'golarchi':                 {'disco': 'HESCO', 'city': 'Badin'},
    'matli':                    {'disco': 'HESCO', 'city': 'Badin'},
    'thatta':                   {'disco': 'HESCO', 'city': 'Thatta'},
    'sujawal':                  {'disco': 'HESCO', 'city': 'Thatta'},
    'mirpur sakro':             {'disco': 'HESCO', 'city': 'Thatta'},
    'jamshoro':                 {'disco': 'HESCO', 'city': 'Jamshoro'},
    'sehwan':                   {'disco': 'HESCO', 'city': 'Jamshoro'},
    'kotri':                    {'disco': 'HESCO', 'city': 'Jamshoro'},
    'dadu':                     {'disco': 'HESCO', 'city': 'Dadu'},
    'johi':                     {'disco': 'HESCO', 'city': 'Dadu'},
    'mehar':                    {'disco': 'HESCO', 'city': 'Dadu'},
    'khairpur':                 {'disco': 'HESCO', 'city': 'Khairpur'},
    'shikarpur':                {'disco': 'HESCO', 'city': 'Shikarpur'},
    'jacobabad':                {'disco': 'HESCO', 'city': 'Jacobabad'},
    'kashmore':                 {'disco': 'HESCO', 'city': 'Kashmore'},
    'kandhkot':                 {'disco': 'HESCO', 'city': 'Kashmore'},
    'ghotki':                   {'disco': 'HESCO', 'city': 'Ghotki'},
    'ubauro':                   {'disco': 'HESCO', 'city': 'Ghotki'},
    'daharki':                  {'disco': 'HESCO', 'city': 'Ghotki'},
    'diplo':                    {'disco': 'HESCO', 'city': 'Tharparkar'},
    'mithi':                    {'disco': 'HESCO', 'city': 'Tharparkar'},
    'islamkot':                 {'disco': 'HESCO', 'city': 'Tharparkar'},
    'nagarparkar':              {'disco': 'HESCO', 'city': 'Tharparkar'},

    # ── SEPCO — Karachi ──────────────────────────────────────────────────────
    'karachi':                  {'disco': 'SEPCO', 'city': 'Karachi'},
    'gulshan iqbal':            {'disco': 'SEPCO', 'city': 'Karachi'},
    'nazimabad':                {'disco': 'SEPCO', 'city': 'Karachi'},
    'north nazimabad':          {'disco': 'SEPCO', 'city': 'Karachi'},
    'gulistan johar':           {'disco': 'SEPCO', 'city': 'Karachi'},
    'dha karachi':              {'disco': 'SEPCO', 'city': 'Karachi'},
    'clifton':                  {'disco': 'SEPCO', 'city': 'Karachi'},
    'pechs':                    {'disco': 'SEPCO', 'city': 'Karachi'},
    'malir':                    {'disco': 'SEPCO', 'city': 'Karachi'},
    'korangi':                  {'disco': 'SEPCO', 'city': 'Karachi'},
    'landhi':                   {'disco': 'SEPCO', 'city': 'Karachi'},
    'orangi town':              {'disco': 'SEPCO', 'city': 'Karachi'},
    'surjani town':             {'disco': 'SEPCO', 'city': 'Karachi'},
    'federal b area':           {'disco': 'SEPCO', 'city': 'Karachi'},
    'bahria town karachi':      {'disco': 'SEPCO', 'city': 'Karachi'},
    'saddar karachi':           {'disco': 'SEPCO', 'city': 'Karachi'},
    'defence karachi':          {'disco': 'SEPCO', 'city': 'Karachi'},
    'clifton karachi':          {'disco': 'SEPCO', 'city': 'Karachi'},
    'zamzama':                  {'disco': 'SEPCO', 'city': 'Karachi'},
    'tariq road':               {'disco': 'SEPCO', 'city': 'Karachi'},
    'lyari':                    {'disco': 'SEPCO', 'city': 'Karachi'},
    'kemari':                   {'disco': 'SEPCO', 'city': 'Karachi'},
    'shah faisal colony':       {'disco': 'SEPCO', 'city': 'Karachi'},
    'manghopir':                {'disco': 'SEPCO', 'city': 'Karachi'},
    'site area':                {'disco': 'SEPCO', 'city': 'Karachi'},
    'new karachi':              {'disco': 'SEPCO', 'city': 'Karachi'},
    'north karachi':            {'disco': 'SEPCO', 'city': 'Karachi'},
    'liaquatabad':              {'disco': 'SEPCO', 'city': 'Karachi'},
    'gulberg karachi':          {'disco': 'SEPCO', 'city': 'Karachi'},
    'model colony':             {'disco': 'SEPCO', 'city': 'Karachi'},
    'bin qasim':                {'disco': 'SEPCO', 'city': 'Karachi'},

    # ── QESCO — Balochistan ──────────────────────────────────────────────────
    'quetta':                   {'disco': 'QESCO', 'city': 'Quetta'},
    'satellite town quetta':    {'disco': 'QESCO', 'city': 'Quetta'},
    'cantt quetta':             {'disco': 'QESCO', 'city': 'Quetta'},
    'sariab':                   {'disco': 'QESCO', 'city': 'Quetta'},
    'kuchlak':                  {'disco': 'QESCO', 'city': 'Quetta'},
    'pishin':                   {'disco': 'QESCO', 'city': 'Pishin'},
    'khanozai':                 {'disco': 'QESCO', 'city': 'Pishin'},
    'turbat':                   {'disco': 'QESCO', 'city': 'Turbat'},
    'khuzdar':                  {'disco': 'QESCO', 'city': 'Khuzdar'},
    'hub':                      {'disco': 'QESCO', 'city': 'Hub'},
    'chaman':                   {'disco': 'QESCO', 'city': 'Chaman'},
    'gwadar':                   {'disco': 'QESCO', 'city': 'Gwadar'},
    'zhob':                     {'disco': 'QESCO', 'city': 'Zhob'},
    'loralai':                  {'disco': 'QESCO', 'city': 'Loralai'},
    'sibi':                     {'disco': 'QESCO', 'city': 'Sibi'},
    'dera bugti':               {'disco': 'QESCO', 'city': 'Dera Bugti'},
    'sui':                      {'disco': 'QESCO', 'city': 'Dera Bugti'},
    'mastung':                  {'disco': 'QESCO', 'city': 'Mastung'},
    'kalat':                    {'disco': 'QESCO', 'city': 'Kalat'},
    'kharan':                   {'disco': 'QESCO', 'city': 'Kharan'},
    'panjgur':                  {'disco': 'QESCO', 'city': 'Panjgur'},
    'nushki':                   {'disco': 'QESCO', 'city': 'Nushki'},
    'dalbandin':                {'disco': 'QESCO', 'city': 'Chagai'},
    'awaran':                   {'disco': 'QESCO', 'city': 'Awaran'},
    'lasbela':                  {'disco': 'QESCO', 'city': 'Lasbela'},
    'uthal':                    {'disco': 'QESCO', 'city': 'Lasbela'},
    'dera murad jamali':        {'disco': 'QESCO', 'city': 'Nasirabad'},
    'nasirabad':                {'disco': 'QESCO', 'city': 'Nasirabad'},
    'jaffarabad':               {'disco': 'QESCO', 'city': 'Jaffarabad'},
    'usta mohammad':            {'disco': 'QESCO', 'city': 'Jaffarabad'},
    'ziarat':                   {'disco': 'QESCO', 'city': 'Ziarat'},
    'harnai':                   {'disco': 'QESCO', 'city': 'Harnai'},
    'qila saifullah':           {'disco': 'QESCO', 'city': 'Qila Saifullah'},
    'muslim bagh':              {'disco': 'QESCO', 'city': 'Qila Saifullah'},
}

# ══════════════════════════════════════════════════════════════════════════════
#  DISCO URLs
# ══════════════════════════════════════════════════════════════════════════════
DISCO_URLS = {
    'LESCO': 'https://www.lesco.gov.pk/Modules/Loadshedding/index.asp',
    'IESCO': 'https://www.iesco.com.pk/index.php/load-shedding-schedule',
    'FESCO': 'https://www.fesco.com.pk/loadshedding-schedule/',
    'GEPCO': 'https://www.gepco.com.pk/loadshedding.php',
    'MEPCO': 'https://www.mepco.com.pk/loadshedding.asp',
    'PESCO': 'https://www.pesco.com.pk/load_shedding/',
    'HESCO': 'https://www.hesco.gov.pk/loadshedding',
    'SEPCO': 'https://www.sepco.com.pk/loadshedding',
    'QESCO': 'https://www.qesco.com.pk/loadshedding',
}

# ══════════════════════════════════════════════════════════════════════════════
#  SMART FALLBACK MAPS
# ══════════════════════════════════════════════════════════════════════════════

# Layer 3a — known city/district names not already in AREAS
CITY_DISCO_MAP = {
    'lahore': 'LESCO', 'sheikhupura': 'LESCO', 'nankana': 'LESCO', 'kasur': 'LESCO',
    'gujranwala': 'GEPCO', 'sialkot': 'GEPCO', 'gujrat': 'GEPCO', 'hafizabad': 'GEPCO',
    'faisalabad': 'FESCO', 'sargodha': 'FESCO', 'jhang': 'FESCO', 'khushab': 'FESCO',
    'multan': 'MEPCO', 'bahawalpur': 'MEPCO', 'sahiwal': 'MEPCO', 'okara': 'MEPCO',
    'rahim yar khan': 'MEPCO', 'lodhran': 'MEPCO', 'khanewal': 'MEPCO',
    'islamabad': 'IESCO', 'rawalpindi': 'IESCO', 'jhelum': 'IESCO',
    'chakwal': 'IESCO', 'attock': 'IESCO',
    'peshawar': 'PESCO', 'abbottabad': 'PESCO', 'mardan': 'PESCO', 'swat': 'PESCO',
    'kohat': 'PESCO', 'mansehra': 'PESCO', 'bannu': 'PESCO', 'swabi': 'PESCO',
    'dir': 'PESCO', 'chitral': 'PESCO', 'buner': 'PESCO', 'nowshera': 'PESCO',
    'karachi': 'SEPCO',
    'hyderabad': 'HESCO', 'sukkur': 'HESCO', 'larkana': 'HESCO',
    'mirpur khas': 'HESCO', 'nawabshah': 'HESCO', 'jacobabad': 'HESCO',
    'quetta': 'QESCO', 'gwadar': 'QESCO', 'turbat': 'QESCO', 'khuzdar': 'QESCO',
    'hub': 'QESCO', 'chaman': 'QESCO', 'zhob': 'QESCO',
}

# Layer 3b — province keyword → default DISCO
PROVINCE_KEYWORDS = {
    'punjab': 'LESCO', 'lahori': 'LESCO',
    'pindi': 'IESCO', 'islamabadi': 'IESCO',
    'kpk': 'PESCO', 'khyber': 'PESCO', 'pakhtunkhwa': 'PESCO',
    'sindh': 'HESCO', 'sindhi': 'HESCO',
    'balochistan': 'QESCO', 'baloch': 'QESCO',
}

DISCO_PROVINCE = {
    'LESCO': 'لاہور / LESCO',   'GEPCO': 'گوجرانوالہ / GEPCO',
    'FESCO': 'فیصل آباد / FESCO', 'MEPCO': 'ملتان / MEPCO',
    'IESCO': 'اسلام آباد / IESCO', 'PESCO': 'پشاور / PESCO',
    'HESCO': 'حیدرآباد / HESCO',  'SEPCO': 'کراچی / SEPCO',
    'QESCO': 'کوئٹہ / QESCO',
}

# ══════════════════════════════════════════════════════════════════════════════
#  INTENT KEYWORDS
# ══════════════════════════════════════════════════════════════════════════════
OUT_WORDS = [
    'bijli gayi', 'bijli band', 'bijli nahi', 'light gayi', 'light band',
    'gayi', 'gai', 'band ho gayi', 'chali gayi', 'nahi hai', 'nahi aayi',
    'بجلی گئی', 'بجلی بند', 'لائٹ گئی', 'load shedding', 'loadshedding',
    'current nahi', 'bijli off', 'gul ho gai', 'gul', 'cut ho gayi',
]
ON_WORDS = [
    'bijli aayi', 'bijli aa gayi', 'light aayi', 'light aa gayi',
    'agayi', 'aa gayi', 'wapis aayi', 'wapas aayi', 'restore',
    'بجلی آئی', 'لائٹ آئی', 'current aa gaya', 'aa gyi', 'aayi',
    'wapis', 'on ho gayi', 'chali aayi',
]
SCHEDULE_WORDS = [
    'schedule', 'timing', 'timings', 'kab aayegi', 'kab aati', 'kab jayegi',
    'kitni der', 'kitna time', 'check karo', 'update', 'batao', 'bata',
    'today', 'aaj', 'status', 'info', 'details', 'plan',
    'کب آئے گی', 'کتنی دیر', 'شیڈول', 'ٹائمنگ', 'بتاؤ',
]
HELP_WORDS = [
    'help', 'مدد', 'menu', 'start', 'hello', 'hi', 'salam', 'assalam',
    'helo', 'hey', 'commands', 'kya karo', 'kaise', 'guide',
]
THANKS_WORDS = [
    'thanks', 'shukriya', 'شکریہ', 'thankyou', 'thank you', 'jazakallah',
    'جزاک اللہ', 'good', 'nice', 'great', 'badhiya', 'zabardast',
]

# ══════════════════════════════════════════════════════════════════════════════
#  3-LAYER AREA LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
def find_area(text):
    """Returns (area_key, area_data, is_approximate)"""
    t = text.lower().strip()

    # Layer 1 — exact match
    if t in AREAS:
        return t, AREAS[t], False

    # Layer 2 — partial match
    for area, data in AREAS.items():
        if area in t or t in area:
            return area, data, False

    # Layer 3a — known city name
    for city, disco in CITY_DISCO_MAP.items():
        if city in t:
            return t, {'disco': disco, 'city': city.title()}, True

    # Layer 3b — province keyword (last resort)
    for kw, disco in PROVINCE_KEYWORDS.items():
        if kw in t:
            return t, {'disco': disco, 'city': t.title()}, True

    return None, None, False

# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def db_save_schedule(area, disco, date, outages, total_hours=0):
    try:
        supabase.table('schedules').upsert(
            {'area': area, 'disco': disco, 'date': str(date),
             'outages': outages, 'total_hours': total_hours},
            on_conflict='area,date'
        ).execute()
        return True
    except Exception as e:
        print(f'db_save error: {e}')
        return False

def db_get_schedule(area):
    try:
        date = now_pkt().strftime('%Y-%m-%d')
        r = supabase.table('schedules').select('*').eq('area', area).eq('date', date).limit(1).execute()
        return r.data[0] if r.data else None
    except:
        return None

def db_log_report(area, event, user_id):
    try:
        supabase.table('crowd_reports').insert({
            'area': area, 'event': event,
            'user_id': user_id, 'reported_at': now_pkt().isoformat()
        }).execute()
        user = db_get_user(user_id)
        if user:
            supabase.table('users').update(
                {'report_count': user.get('report_count', 0) + 1,
                 'last_seen': now_pkt().isoformat()}
            ).eq('user_id', user_id).execute()
        return True
    except:
        return False

def db_get_crowd_signal(area, minutes=30):
    try:
        since = (now_pkt() - timedelta(minutes=minutes)).isoformat()
        r = supabase.table('crowd_reports').select('event').eq('area', area).gte('reported_at', since).execute()
        reports = r.data or []
        out      = sum(1 for x in reports if x['event'] == 'out')
        restored = sum(1 for x in reports if x['event'] == 'restored')
        if out >= 3:        signal = 'confirmed_out'
        elif restored >= 3: signal = 'confirmed_restored'
        elif out > 0:       signal = 'likely_out'
        elif restored > 0:  signal = 'likely_restored'
        else:               signal = 'no_data'
        return {'signal': signal, 'out_count': out, 'restored_count': restored}
    except:
        return {'signal': 'no_data', 'out_count': 0, 'restored_count': 0}

def db_upsert_user(user_id, area=None, disco=None):
    try:
        data = {'user_id': user_id, 'last_seen': now_pkt().isoformat()}
        if area:  data['area']  = area
        if disco: data['disco'] = disco
        supabase.table('users').upsert(data, on_conflict='user_id').execute()
    except:
        pass

def db_get_user(user_id):
    try:
        r = supabase.table('users').select('*').eq('user_id', user_id).limit(1).execute()
        return r.data[0] if r.data else None
    except:
        return None

# ══════════════════════════════════════════════════════════════════════════════
#  SCRAPER
# ══════════════════════════════════════════════════════════════════════════════
def scrape_schedule(area, disco):
    today  = now_pkt().strftime('%Y-%m-%d')
    sample = [
        {'start': '08:00', 'end': '10:00', 'source': 'sample'},
        {'start': '14:00', 'end': '16:00', 'source': 'sample'},
        {'start': '20:00', 'end': '22:00', 'source': 'sample'},
    ]
    try:
        url     = DISCO_URLS.get(disco, DISCO_URLS['LESCO'])
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp    = requests.get(url, headers=headers, timeout=15)
        soup    = BeautifulSoup(resp.text, 'lxml')
        text    = soup.get_text(separator=' ')
        matches = re.findall(r'(\d{1,2}:\d{2})\s*(?:-|to)\s*(\d{1,2}:\d{2})', text, re.I)
        outages = [{'start': s, 'end': e, 'source': 'official'} for s, e in dict.fromkeys(matches)]
        if outages:
            total_h = sum(
                (datetime.strptime(o['end'], '%H:%M') - datetime.strptime(o['start'], '%H:%M')).seconds / 3600
                for o in outages
            )
            db_save_schedule(area, disco, today, outages, round(total_h, 1))
            return outages, round(total_h, 1)
    except Exception as e:
        print(f'Scraper error: {e}')
    db_save_schedule(area, disco, today, sample, 6)
    return sample, 6

# ══════════════════════════════════════════════════════════════════════════════
#  REPLY BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def build_reply(area, schedule, crowd, is_approximate=False, disco=None):
    outages   = schedule.get('outages', []) if schedule else []
    total_h   = schedule.get('total_hours', 0) if schedule else 0
    date      = now_pkt().strftime('%d %b %Y')
    now_h     = now_pkt().hour
    area_name = area.title()

    lines = [
        f'⚡ *{area_name}* — {date}',
        f'آج کل *{total_h} گھنٹے* کی لوڈ شیڈنگ ہے 😤',
        '',
    ]
    if is_approximate and disco:
        province_label = DISCO_PROVINCE.get(disco, disco)
        lines.append(f'_⚠️ {province_label} کا عمومی شیڈول — آپ کے علاقے میں تھوڑا فرق ہو سکتا ہے_')
        lines.append('')

    lines.append('🕐 *شیڈول:*')

    upcoming_warning = None
    for o in outages:
        try:
            sh   = int(o['start'].split(':')[0])
            diff = sh - now_h
            if diff < 0:
                icon, label = '⚫', '(ہو چکی)'
            elif diff == 0:
                icon, label = '🔴', '(ابھی!)'
            else:
                icon, label = '🔴', ''
            if 0 < diff <= 1 and not upcoming_warning:
                mins = int(diff * 60)
                upcoming_warning = f'⚠️ بھائی! *{mins} منٹ میں* بجلی جانے والی ہے — موبائل چارج کر لو! 🔋'
        except:
            icon, label = '🔴', ''
        lines.append(f'  {icon} {o["start"]} — {o["end"]} {label}'.strip())

    lines.append('')
    sig = crowd['signal']
    if sig == 'confirmed_out':
        lines.append(f'🔴 *ابھی بجلی نہیں* — {crowd["out_count"]} لوگوں نے تصدیق کی')
    elif sig == 'confirmed_restored':
        lines.append(f'✅ *ابھی بجلی ہے* — {crowd["restored_count"]} لوگوں نے بتایا')
    elif sig == 'likely_out':
        lines.append('🟠 لگتا ہے ابھی بجلی نہیں ہے')
    elif sig == 'likely_restored':
        lines.append('🟡 شاید بجلی آ گئی ہے')
    else:
        lines.append('📊 ابھی کوئی لائیو رپورٹ نہیں')

    if upcoming_warning:
        lines += ['', upcoming_warning]

    lines += [
        '',
        '📣 *آپ بھی مدد کریں:*',
        '  بجلی گئی؟ → *بجلی گئی* لکھیں',
        '  بجلی آئی؟ → *بجلی آئی* لکھیں',
        '',
        '🤖 _LoadSheddingPK — سب کی مدد کریں_ 🇵🇰',
    ]
    return '\n'.join(lines)

# ══════════════════════════════════════════════════════════════════════════════
#  MESSAGE TEMPLATES  — friendly, guided, conversational
# ══════════════════════════════════════════════════════════════════════════════
def msg_welcome():
    """First time user — one simple ask, no walls of text."""
    greetings = [
        'السلام علیکم! ⚡',
        'آداب! ⚡',
        'ہیلو! ⚡',
    ]
    return (
        f'{random.choice(greetings)}\n\n'
        'میں *LoadSheddingPK* ہوں 🇵🇰\n'
        'بجلی کب آئے گی؟ میں بتاتا ہوں!\n\n'
        '👇 *بس اپنا علاقہ لکھیں:*\n'
        '_مثال: Gulberg, DHA, Clifton, Hayatabad_'
    )

def msg_welcome_back(area):
    """Returning user who types something unrecognized — remind them."""
    return (
        f'بھائی، آپ کا علاقہ *{area.title()}* سیو ہے ⚡\n\n'
        'کیا چاہیے؟\n'
        '• شیڈول → *schedule* لکھیں\n'
        '• بجلی گئی → *بجلی گئی* لکھیں\n'
        '• بجلی آئی → *بجلی آئی* لکھیں\n'
        '• علاقہ بدلنا ہے → نیا علاقہ لکھیں'
    )

def msg_help():
    return (
        '⚡ *LoadSheddingPK — کیسے استعمال کریں؟*\n\n'
        '1️⃣ اپنا علاقہ لکھیں\n'
        '   _Gulberg / DHA Lahore / Clifton / Hayatabad_\n\n'
        '2️⃣ شیڈول دیکھنے کے لیے\n'
        '   *schedule* یا *batao* لکھیں\n\n'
        '3️⃣ بجلی گئی؟\n'
        '   *بجلی گئی* لکھیں\n\n'
        '4️⃣ بجلی آئی؟\n'
        '   *بجلی آئی* لکھیں\n\n'
        '🗺️ پورا پاکستان سپورٹ ہے —\n'
        'لاہور، کراچی، پشاور، کوئٹہ، ہر جگہ! 🇵🇰'
    )

def msg_no_area_set():
    """User tried to report or check without setting area first — guide them gently."""
    openers = [
        'ارے بھائی! 😄',
        'یار! 😅',
        'اوہو! 🙂',
    ]
    return (
        f'{random.choice(openers)}\n\n'
        'پہلے اپنا علاقہ بتائیں تاکہ میں آپ کی مدد کر سکوں 👇\n\n'
        'بس لکھیں جیسے:\n'
        '*Gulberg*  یا  *DHA Lahore*  یا  *Clifton*'
    )

def msg_area_saved_first_time(area):
    """Show right after first area is set — instant gratification."""
    return (
        f'✅ *{area.title()}* — سیو ہو گیا!\n\n'
        'ابھی آپ کا شیڈول نکال رہا ہوں... ⏳'
    )

def msg_out_confirmed(area):
    openers = ['ہاں بھائی، نوٹ کر لیا! 📋', 'ٹھیک ہے، رپورٹ مل گئی! ✅', 'شکریہ بتانے کا! 🙏']
    return (
        f'{random.choice(openers)}\n'
        f'*{area.title()}* — بجلی بند ✅\n\n'
        'جب واپس آئے تو *بجلی آئی* لکھنا —\n'
        'باقی لوگوں کو بھی پتہ چلے گا! 🤝'
    )

def msg_restored_confirmed(area):
    return (
        f'✨ واہ! *{area.title()}* میں بجلی آ گئی!\n'
        'شکریہ بتانے کا — آپ کی رپورٹ سے دوسروں کو مدد ملتی ہے 🙏\n\n'
        '_LoadSheddingPK_ 🇵🇰'
    )

def msg_thanks():
    replies = [
        'آپ کا شکریہ! 🙏 ہماری کمیونٹی آپ سے چلتی ہے 💪',
        'بہت خوب! آپ جیسے لوگ ہی اس app کو کام کا بناتے ہیں 😊',
        'جزاک اللہ! رپورٹ کرتے رہیں 🤝',
    ]
    return random.choice(replies)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN HANDLER
# ══════════════════════════════════════════════════════════════════════════════
def handle_message(text, phone):
    t   = text.lower().strip()
    uid = hashlib.md5(phone.encode()).hexdigest()[:10]

    if any(w in t for w in THANKS_WORDS):
        return msg_thanks()

    if any(w in t for w in OUT_WORDS):
        user = db_get_user(uid)
        area = user['area'] if user and user.get('area') else None
        if not area:
            return msg_no_area_set()
        db_log_report(area, 'out', uid)
        return msg_out_confirmed(area)

    if any(w in t for w in ON_WORDS):
        user = db_get_user(uid)
        area = user['area'] if user and user.get('area') else None
        if not area:
            return msg_no_area_set()
        db_log_report(area, 'restored', uid)
        return msg_restored_confirmed(area)

    if any(w in t for w in HELP_WORDS):
        return msg_help()

    if any(w in t for w in SCHEDULE_WORDS):
        user = db_get_user(uid)
        area = user['area'] if user and user.get('area') else None
        if not area:
            return msg_no_area_set()
        s = db_get_schedule(area)
        if not s:
            disco = AREAS.get(area, {}).get('disco', 'LESCO')
            outages, total_h = scrape_schedule(area, disco)
            s = {'area': area, 'outages': outages, 'total_hours': total_h}
        c = db_get_crowd_signal(area)
        return build_reply(area, s, c)

    # 3-layer area lookup
    area_name, area_data, is_approx = find_area(t)
    if area_data:
        disco = area_data['disco']
        is_new_user = db_get_user(uid) is None
        db_upsert_user(uid, area=area_name, disco=disco)
        schedule = db_get_schedule(area_name)
        if not schedule:
            outages, total_h = scrape_schedule(area_name, disco)
            schedule = {'area': area_name, 'outages': outages, 'total_hours': total_h}
        crowd = db_get_crowd_signal(area_name)
        reply = build_reply(area_name, schedule, crowd, is_approximate=is_approx, disco=disco)
        if is_new_user:
            return msg_area_saved_first_time(area_name) + '\n\n' + reply
        return reply

    # Returning user — unrecognised message, show friendly reminder + their schedule
    user = db_get_user(uid)
    if user and user.get('area'):
        a     = user['area']
        disco = AREAS.get(a, {}).get('disco', 'LESCO')
        s     = db_get_schedule(a)
        if not s:
            outages, total_h = scrape_schedule(a, disco)
            s = {'area': a, 'outages': outages, 'total_hours': total_h}
        c = db_get_crowd_signal(a)
        return msg_welcome_back(a) + '\n\n' + build_reply(a, s, c)

    return msg_welcome()

# ══════════════════════════════════════════════════════════════════════════════
#  FLASK ROUTES
# ══════════════════════════════════════════════════════════════════════════════
@app.route('/bot', methods=['POST'])
def bot():
    incoming = request.form.get('Body', '').strip()
    sender   = request.form.get('From', '')
    print(f'[{now_pkt().strftime("%H:%M")}] {sender[-10:]}: {incoming}')
    reply = handle_message(incoming, sender)
    resp  = MessagingResponse()
    resp.message(reply)
    return str(resp)

@app.route('/health')
def health():
    return {'status': 'ok', 'time': now_pkt().isoformat()}, 200

@app.route('/')
def home():
    return '<h2>⚡ LoadSheddingPK Bot is running! 🇵🇰</h2>', 200
    @app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == os.environ.get('VERIFY_TOKEN'):
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        text = msg['text']['body']
        phone = msg['from']
        reply = handle_message(text, phone)
        # Send reply via Meta API
        token = os.environ.get('WHATSAPP_TOKEN')
        phone_id = os.environ.get('PHONE_NUMBER_ID')
        requests.post(
            f'https://graph.facebook.com/v18.0/{phone_id}/messages',
            headers={'Authorization': f'Bearer {token}'},
            json={'messaging_product': 'whatsapp', 'to': phone, 'text': {'body': reply}}
        )
    except Exception as e:
        print(f'Webhook error: {e}')
    return 'OK', 200

if __name__ == '__main__':
    print('⚡ LoadSheddingPK Bot starting...')
    print('   http://localhost:5000/health')
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
