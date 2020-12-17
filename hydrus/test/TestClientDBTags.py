import os
import random
import time
import unittest

from hydrus.core import HydrusConstants as HC
from hydrus.core import HydrusData
from hydrus.core import HydrusGlobals as HG

from hydrus.client import ClientConstants as CC
from hydrus.client import ClientDB
from hydrus.client import ClientSearch
from hydrus.client import ClientServices
from hydrus.client.importing import ClientImportFileSeeds
from hydrus.client.metadata import ClientTags

from hydrus.test import TestController

IRL_PARENT_PAIRS = {
    ( 'series:diablo', 'studio:blizzard entertainment' ),
    ( 'series:hearthstone', 'studio:blizzard entertainment' ),
    ( 'series:heroes of the storm', 'studio:blizzard entertainment' ),
    ( 'series:overwatch', 'studio:blizzard entertainment' ),
    ( 'series:starcraft', 'studio:blizzard entertainment' ),
    ( 'series:warcraft', 'studio:blizzard entertainment' ),
    ( 'character:li-ming the rebellious wizard', 'series:diablo' ),
    ( 'series:diablo ii', 'series:diablo' ),
    ( 'series:diablo iii', 'series:diablo' ),
    ( 'character:akande "doomfist" ogundimu', 'series:overwatch' ),
    ( 'character:aleksandra "zarya" zaryanova', 'series:overwatch' ),
    ( 'character:amélie "widowmaker" lacroix', 'series:overwatch' ),
    ( 'character:ana amari', 'series:overwatch' ),
    ( 'character:brian (overwatch)', 'series:overwatch' ),
    ( 'character:brigitte lindholm', 'series:overwatch' ),
    ( 'character:dr. angela "mercy" ziegler', 'series:overwatch' ),
    ( 'character:efi oladele', 'series:overwatch' ),
    ( 'character:elizabeth caledonia "calamity" ashe', 'series:overwatch' ),
    ( 'character:fareeha "pharah" amari', 'series:overwatch' ),
    ( 'character:gabriel "reaper" reyes', 'series:overwatch' ),
    ( 'character:genji shimada', 'series:overwatch' ),
    ( 'character:hana "d.va" song', 'series:overwatch' ),
    ( 'character:hanzo shimada', 'series:overwatch' ),
    ( 'character:jack "soldier 76" morrison', 'series:overwatch' ),
    ( 'character:jamison "junkrat" fawkes', 'series:overwatch' ),
    ( 'character:jesse mccree', 'series:overwatch' ),
    ( 'character:katya volskaya', 'series:overwatch' ),
    ( 'character:katya volskaya\'s daughter', 'series:overwatch' ),
    ( 'character:lena "tracer" oxton', 'series:overwatch' ),
    ( 'character:lúcio correia dos santos', 'series:overwatch' ),
    ( 'character:mako "roadhog" rutledge', 'series:overwatch' ),
    ( 'character:mei (overwatch)', 'series:overwatch' ),
    ( 'character:mei-ling zhou, "mei"', 'series:overwatch' ),
    ( 'character:moira o’deorain', 'series:overwatch' ),
    ( 'character:olivia "sombra" colomar', 'series:overwatch' ),
    ( 'character:orisa', 'series:overwatch' ),
    ( 'character:reinhardt wilhelm', 'series:overwatch' ),
    ( 'character:satya "symmetra" vaswani', 'series:overwatch' ),
    ( 'character:sombra (overwatch)', 'series:overwatch' ),
    ( 'character:sst laboratories siege automaton e54, “bastion"', 'series:overwatch' ),
    ( 'character:tekhartha zenyatta', 'series:overwatch' ),
    ( 'character:timmy (overwatch)', 'series:overwatch' ),
    ( 'character:torbjörn lindholm', 'series:overwatch' ),
    ( 'character:“bastion", sst laboratories siege automaton e54', 'series:overwatch' ),
    ( 'character:jim raynor', 'series:starcraft' ),
    ( 'character:nova terra', 'series:starcraft' ),
    ( 'character:queen of blades', 'series:starcraft' ),
    ( 'character:sarah kerrigan', 'series:starcraft' ),
    ( 'character:alexstrasza', 'series:warcraft' ),
    ( 'character:alleria windrunner', 'series:warcraft' ),
    ( 'character:eonar, the life binder', 'series:warcraft' ),
    ( 'character:jaina proudmoore', 'series:warcraft' ),
    ( 'character:lady liadrin', 'series:warcraft' ),
    ( 'character:queen azshara', 'series:warcraft' ),
    ( 'character:sylvanas windrunner', 'series:warcraft' ),
    ( 'character:tyrande whisperwind', 'series:warcraft' ),
    ( 'series:world of warcraft', 'series:warcraft' ),
    ( 'species:night elf', 'series:warcraft' ),
    ( 'species:tauren', 'series:warcraft' )
}

IRL_SIBLING_PAIRS = {
    ( 'character:akande ogundimu', 'character:akande "doomfist" ogundimu' ),
    ( 'character:doomfist', 'character:akande "doomfist" ogundimu' ),
    ( 'character:doomfist (overwatch)', 'character:akande "doomfist" ogundimu' ),
    ( 'doomfist', 'character:akande "doomfist" ogundimu' ),
    ( 'doomfist (overwatch)', 'character:akande "doomfist" ogundimu' ),
    ( 'doomfist (overwatch) (cosplay)', 'character:akande "doomfist" ogundimu' ),
    ( 'doomfist_(overwatch)', 'character:akande "doomfist" ogundimu' ),
    ( 'champion zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:aleksandra "zarya" zaryanova (overwatch)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:arctic zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:barbarian zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:barbarian zarya (overwatch)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:champion zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:champion zarya (overwatch)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:cybergoth zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:industrial zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:thunder guard zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:totally 80\'s zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:zarya (overwatch) (cosplay)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'cybergoth zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'industrial zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'totally 80\'s zarya', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya (cosplay)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya (heros of the storm)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya (overwatch)1girl', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya (overwatch) (cosplay)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya (overwatch) cosplay', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya (overwatch)female', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_(cosplay)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_(heros_of_the_storm)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_(overwatch)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_(overwatch)1girl', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_(overwatch)_(cosplay)', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_(overwatch)_cosplay', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zarya_overwatch', 'character:aleksandra "zarya" zaryanova' ),
    ( 'zaryanova', 'character:aleksandra "zarya" zaryanova' ),
    ( 'character:alextrasza', 'character:alexstrasza' ),
    ( 'character:alexstrasza', 'character:alextrasza the life-binder' ),
    ( 'alleria windrunner', 'character:alleria windrunner' ),
    ( 'amelia lacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'amelie lacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'amélie "windowmaker" lacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'amélie lacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'amélie_"windowmaker"_lacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'amélielacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'character:amélie "widowmaker" lacroix (née guillard)', 'character:amélie "widowmaker" lacroix' ),
    ( 'character:amélie "widowmaker" lacroix (overwatch)', 'character:amélie "widowmaker" lacroix' ),
    ( 'character:amélie lacroix', 'character:amélie "widowmaker" lacroix' ),
    ( 'character:widowmaker(overwatch)', 'character:amélie "widowmaker" lacroix' ),
    ( 'overwatch widowmaker', 'character:amélie "widowmaker" lacroix' ),
    ( 'widowmaker (overwatch', 'character:amélie "widowmaker" lacroix' ),
    ( 'widowmaker overwatch', 'character:amélie "widowmaker" lacroix' ),
    ( 'widowmaker(overwatch)', 'character:amélie "widowmaker" lacroix' ),
    ( 'widowmaker_(overwatch)', 'character:amélie "widowmaker" lacroix' ),
    ( 'widowmaker_(overwatch_', 'character:amélie "widowmaker" lacroix' ),
    ( 'ウィドウメイカー', 'character:amélie "widowmaker" lacroix' ),
    ( 'ana (overwatch)', 'character:ana amari' ),
    ( 'ana amari', 'character:ana amari' ),
    ( 'ana_(overwatch)', 'character:ana amari' ),
    ( 'ana_amari', 'character:ana amari' ),
    ( 'character:ana (overwatch)', 'character:ana amari' ),
    ( 'character:ana amari (cosplay)', 'character:ana amari' ),
    ( 'character:ana amari (overwatch)', 'character:ana amari' ),
    ( 'brian (overwatch)', 'character:brian (overwatch)' ),
    ( 'brigitte (overwatch)', 'character:brigitte lindholm' ),
    ( 'brigitte lindholm', 'character:brigitte lindholm' ),
    ( 'brigitte lindholmn', 'character:brigitte lindholm' ),
    ( 'brigitte_(overwatch)', 'character:brigitte lindholm' ),
    ( 'brigitte_lindholm', 'character:brigitte lindholm' ),
    ( 'brigitte_lindholmn', 'character:brigitte lindholm' ),
    ( 'brigittelindholm', 'character:brigitte lindholm' ),
    ( 'character:brigitte (overwatch)', 'character:brigitte lindholm' ),
    ( 'character:brigitte lindholm (overwatch)', 'character:brigitte lindholm' ),
    ( 'character:brigitte_(overwatch)', 'character:brigitte lindholm' ),
    ( 'overwatch brigitte', 'character:brigitte lindholm' ),
    ( 'angela_ziegler', 'character:dr. angela "mercy" ziegler' ),
    ( 'character:angela "mercy" ziegler', 'character:dr. angela "mercy" ziegler' ),
    ( 'character:mercy', 'character:dr. angela "mercy" ziegler' ),
    ( 'character:mercy (mercy)', 'character:dr. angela "mercy" ziegler' ),
    ( 'character:mercy (overwatch)', 'character:dr. angela "mercy" ziegler' ),
    ( 'dr angela ziegler', 'character:dr. angela "mercy" ziegler' ),
    ( 'mercy', 'character:dr. angela "mercy" ziegler' ),
    ( 'mercy (mercy)', 'character:dr. angela "mercy" ziegler' ),
    ( 'mercy_(mercy)', 'character:dr. angela "mercy" ziegler' ),
    ( 'overwatch mercy', 'character:dr. angela "mercy" ziegler' ),
    ( 'character:efi oladele (overwatch)', 'character:efi oladele' ),
    ( 'character:efi_oladele', 'character:efi oladele' ),
    ( 'efi oladele', 'character:efi oladele' ),
    ( 'efi oladele (overwatch)', 'character:efi oladele' ),
    ( 'efi_oladele', 'character:efi oladele' ),
    ( 'efi_oladele_(overwatch)', 'character:efi oladele' ),
    ( 'efi_oladelel', 'character:efi oladele' ),
    ( 'ashe (overwatch)', 'character:elizabeth caledonia "calamity" ashe' ),
    ( 'ashe_(overwatch)', 'character:elizabeth caledonia "calamity" ashe' ),
    ( 'character:elizabeth ashe', 'character:elizabeth caledonia "calamity" ashe' ),
    ( 'character:elizabeth caledonia ashe', 'character:elizabeth caledonia "calamity" ashe' ),
    ( 'character:elizabeth caledonia “calamity” ashe', 'character:elizabeth caledonia "calamity" ashe' ),
    ( 'elizabeth caledonia ashe', 'character:elizabeth caledonia "calamity" ashe' ),
    ( '애쉬', 'character:elizabeth caledonia "calamity" ashe' ),
    ( 'character:fareeha "pharah" amari (overwatch)', 'character:fareeha "pharah" amari' ),
    ( 'character:pharah', 'character:fareeha "pharah" amari' ),
    ( 'character:pharah (ow)', 'character:fareeha "pharah" amari' ),
    ( 'character:pharah_(overwatch)', 'character:fareeha "pharah" amari' ),
    ( 'overwatch pharah', 'character:fareeha "pharah" amari' ),
    ( 'pharah', 'character:fareeha "pharah" amari' ),
    ( 'pharah amari', 'character:fareeha "pharah" amari' ),
    ( 'pharah overwatch', 'character:fareeha "pharah" amari' ),
    ( 'pharah_(overwatch)', 'character:fareeha "pharah" amari' ),
    ( 'pharah_amari', 'character:fareeha "pharah" amari' ),
    ( 'character:gabriel "reaper" reyes (overwatch)', 'character:gabriel "reaper" reyes' ),
    ( 'character:gabriel reyes', 'character:gabriel "reaper" reyes' ),
    ( 'character:gabriel reyes, "reaper" (overwatch)', 'character:gabriel "reaper" reyes' ),
    ( 'character:reaper (overwatch)', 'character:gabriel "reaper" reyes' ),
    ( 'character:reaper (overwatch) (cosplay)', 'character:gabriel "reaper" reyes' ),
    ( 'character:reaper_(overwatch)', 'character:gabriel "reaper" reyes' ),
    ( 'gabriel reyes', 'character:gabriel "reaper" reyes' ),
    ( 'reaper (cosplay)', 'character:gabriel "reaper" reyes' ),
    ( 'reaper (overwatch', 'character:gabriel "reaper" reyes' ),
    ( 'reaper (overwatch) (cosplay)', 'character:gabriel "reaper" reyes' ),
    ( 'reaper overwatch', 'character:gabriel "reaper" reyes' ),
    ( 'reaper_(overwatch)', 'character:gabriel "reaper" reyes' ),
    ( 'reaper_(overwatch)_(cosplay)', 'character:gabriel "reaper" reyes' ),
    ( 'vampire reaper (cosplay)', 'character:gabriel "reaper" reyes' ),
    ( 'blackwatch genji', 'character:genji shimada' ),
    ( 'character:blackwatch genji', 'character:genji shimada' ),
    ( 'character:genji (overwatch)', 'character:genji shimada' ),
    ( 'character:genji shimada (overwatch)', 'character:genji shimada' ),
    ( 'character:invalid subtag " genji shimada"', 'character:genji shimada' ),
    ( 'character:nomad genji', 'character:genji shimada' ),
    ( 'character:shimada genji', 'character:genji shimada' ),
    ( 'character:sparrow genji', 'character:genji shimada' ),
    ( 'character:sparrow genji (overwatch)', 'character:genji shimada' ),
    ( 'character:young genji', 'character:genji shimada' ),
    ( 'character:young genji (overwatch)', 'character:genji shimada' ),
    ( 'genji (overwatch', 'character:genji shimada' ),
    ( 'genji (overwatch)', 'character:genji shimada' ),
    ( 'genji (overwatch) (cosplay)', 'character:genji shimada' ),
    ( 'genji shiimada', 'character:genji shimada' ),
    ( 'genji shimada', 'character:genji shimada' ),
    ( 'genji_(overwatch)', 'character:genji shimada' ),
    ( 'genji_(overwatch)_(cosplay)', 'character:genji shimada' ),
    ( 'genji_shimada', 'character:genji shimada' ),
    ( 'genjii (overwatch)', 'character:genji shimada' ),
    ( 'genjii_(cosplay)', 'character:genji shimada' ),
    ( 'genjii_(overwatch)', 'character:genji shimada' ),
    ( 'genjishimada', 'character:genji shimada' ),
    ( 'hydrus invalid tag:"character: genji shimada (overwatch)"', 'character:genji shimada' ),
    ( 'hydrus invalid tag:"character: genji shimada"', 'character:genji shimada' ),
    ( 'sentai genji', 'character:genji shimada' ),
    ( 'shimada genji', 'character:genji shimada' ),
    ( 'character:d va', 'character:hana "d.va" song' ),
    ( 'character:d.va (overwatch)', 'character:hana "d.va" song' ),
    ( 'character:hana "d.va" song (overwatch)', 'character:hana "d.va" song' ),
    ( 'd va', 'character:hana "d.va" song' ),
    ( 'd\'va', 'character:hana "d.va" song' ),
    ( 'd-va', 'character:hana "d.va" song' ),
    ( 'd.va (character)', 'character:hana "d.va" song' ),
    ( 'd.va (hana song)', 'character:hana "d.va" song' ),
    ( 'd.va overwatch', 'character:hana "d.va" song' ),
    ( 'd.va(overwatch)', 'character:hana "d.va" song' ),
    ( 'd.va_(gremlin)', 'character:hana "d.va" song' ),
    ( 'd.va_(overwatch)', 'character:hana "d.va" song' ),
    ( 'd_va', 'character:hana "d.va" song' ),
    ( 'casual hanzo', 'character:hanzo shimada' ),
    ( 'character:demon hanzo (overwatch)', 'character:hanzo shimada' ),
    ( 'character:hanzo shimada (overwatch)', 'character:hanzo shimada' ),
    ( 'character:hanzo_(overwatch)', 'character:hanzo shimada' ),
    ( 'character:invalid subtag " hanzo shimada"', 'character:hanzo shimada' ),
    ( 'character:okami hanzo', 'character:hanzo shimada' ),
    ( 'character:okami hanzo (overwatch)', 'character:hanzo shimada' ),
    ( 'character:shimada hanzo', 'character:hanzo shimada' ),
    ( 'character:young hanzo', 'character:hanzo shimada' ),
    ( 'character:young master hanzo', 'character:hanzo shimada' ),
    ( 'character:young master hanzo (overwatch)', 'character:hanzo shimada' ),
    ( 'demon hanzo', 'character:hanzo shimada' ),
    ( 'hanzo (overwatch', 'character:hanzo shimada' ),
    ( 'hanzo (overwatch) (cosplay)', 'character:hanzo shimada' ),
    ( 'hanzo overwatch', 'character:hanzo shimada' ),
    ( 'hanzo_(overwatch)', 'character:hanzo shimada' ),
    ( 'hanzo_(overwatch)_(cosplay)', 'character:hanzo shimada' ),
    ( 'hanzo_shimada', 'character:hanzo shimada' ),
    ( 'hanzooverwatch', 'character:hanzo shimada' ),
    ( 'hydrus invalid tag:"character: hanzo shimada"', 'character:hanzo shimada' ),
    ( 'lone wolf hanzo', 'character:hanzo shimada' ),
    ( 'okami hanzo', 'character:hanzo shimada' ),
    ( 'young master hanzo', 'character:hanzo shimada' ),
    ( 'character:immortal soldier 76', 'character:jack "soldier 76" morrison' ),
    ( 'character:jack "soldier 76"morrison', 'character:jack "soldier 76" morrison' ),
    ( 'character:soldier:76 (overwatch)', 'character:jack "soldier 76" morrison' ),
    ( 'character:soldier: 76 (overwatch) (cosplay)', 'character:jack "soldier 76" morrison' ),
    ( 'character:strike commander morrison', 'character:jack "soldier 76" morrison' ),
    ( 'character:strike commander morrison (overwatch)', 'character:jack "soldier 76" morrison' ),
    ( 'character:strike-commander morrison', 'character:jack "soldier 76" morrison' ),
    ( 'soldier_76', 'character:jack "soldier 76" morrison' ),
    ( 'strike commander morrison', 'character:jack "soldier 76" morrison' ),
    ( 'character:jaina proudemoore', 'character:jaina proudmoore' ),
    ( 'character:jaina proudmoore (warcraft)', 'character:jaina proudmoore' ),
    ( 'character:jaina proudmore', 'character:jaina proudmoore' ),
    ( 'character:jaina_proudmoore', 'character:jaina proudmoore' ),
    ( 'jaina proudmoore', 'character:jaina proudmoore' ),
    ( 'jaina proudmore', 'character:jaina proudmoore' ),
    ( 'jaina_proudmoore', 'character:jaina proudmoore' ),
    ( 'jainaproudmoore', 'character:jaina proudmoore' ),
    ( 'character:dr. junkenstein junkrat (overwatch)', 'character:jamison "junkrat" fawkes' ),
    ( 'character:firework junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'character:firework junkrat (overwatch)', 'character:jamison "junkrat" fawkes' ),
    ( 'character:fool junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'character:hayseed junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'character:hayseed junkrat (overwatch)', 'character:jamison "junkrat" fawkes' ),
    ( 'character:jamison "junkrat" fawkes (overwatch)', 'character:jamison "junkrat" fawkes' ),
    ( 'character:jamison fawkes', 'character:jamison "junkrat" fawkes' ),
    ( 'character:jester junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'character:jester junkrat (overwatch)', 'character:jamison "junkrat" fawkes' ),
    ( 'character:junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'character:junkrat (overwatch) (cosplay)', 'character:jamison "junkrat" fawkes' ),
    ( 'firework junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'hayseed junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'jamison fawkes', 'character:jamison "junkrat" fawkes' ),
    ( 'jamison_fawkes', 'character:jamison "junkrat" fawkes' ),
    ( 'jester junkrat', 'character:jamison "junkrat" fawkes' ),
    ( 'junkrat (overwatch) (cosplay)', 'character:jamison "junkrat" fawkes' ),
    ( 'junkrat_(overwatch)', 'character:jamison "junkrat" fawkes' ),
    ( 'junkrat_(overwatch)_(cosplay)', 'character:jamison "junkrat" fawkes' ),
    ( 'american mccree', 'character:jesse mccree' ),
    ( 'blackwatch mccree', 'character:jesse mccree' ),
    ( 'character:american mccree', 'character:jesse mccree' ),
    ( 'character:blackwatch mccree', 'character:jesse mccree' ),
    ( 'character:gambler mccree', 'character:jesse mccree' ),
    ( 'character:gambler mccree (overwatch)', 'character:jesse mccree' ),
    ( 'character:jesse mccree (overwatch)', 'character:jesse mccree' ),
    ( 'character:lifeguard mccree', 'character:jesse mccree' ),
    ( 'character:lifeguard mccree (overwatch)', 'character:jesse mccree' ),
    ( 'character:mccree', 'character:jesse mccree' ),
    ( 'character:mccree (overwatch) (cosplay)', 'character:jesse mccree' ),
    ( 'character:mccree (overwatch) cosplay', 'character:jesse mccree' ),
    ( 'character:mystery man mccree', 'character:jesse mccree' ),
    ( 'character:riverboat mccree', 'character:jesse mccree' ),
    ( 'character:van helsing mccree', 'character:jesse mccree' ),
    ( 'character:van helsing mccree (overwatch)', 'character:jesse mccree' ),
    ( 'jesse mccree (cosplay)', 'character:jesse mccree' ),
    ( 'jesse_mccree', 'character:jesse mccree' ),
    ( 'lifeguard mccree', 'character:jesse mccree' ),
    ( 'magistrate mccree', 'character:jesse mccree' ),
    ( 'mccree (overwatch', 'character:jesse mccree' ),
    ( 'mccree (overwatch) (cosplay)', 'character:jesse mccree' ),
    ( 'mccree (overwatch) cosplay', 'character:jesse mccree' ),
    ( 'mccree(cosplay)', 'character:jesse mccree' ),
    ( 'mccree_(overwatch)', 'character:jesse mccree' ),
    ( 'mccree_(overwatch)_(cosplay)', 'character:jesse mccree' ),
    ( 'van helsing mccree', 'character:jesse mccree' ),
    ( 'jim raynor', 'character:jim raynor' ),
    ( 'katya volskaya', 'character:katya volskaya' ),
    ( 'katya volskaya\'s daughter', 'character:katya volskaya\'s daughter' ),
    ( 'lady liadrin', 'character:lady liadrin' ),
    ( 'character:lena "tracer" oxton (overwatch)', 'character:lena "tracer" oxton' ),
    ( 'character:tracer (character)', 'character:lena "tracer" oxton' ),
    ( 'character:tracer (cosplay)', 'character:lena "tracer" oxton' ),
    ( 'character:tracer (overwatch) (cosplay)', 'character:lena "tracer" oxton' ),
    ( 'character:tracer (ow)', 'character:lena "tracer" oxton' ),
    ( 'character:tracer_(overwatch)', 'character:lena "tracer" oxton' ),
    ( 'lea oxton', 'character:lena "tracer" oxton' ),
    ( 'lena "tracer" oxton (overwatch)', 'character:lena "tracer" oxton' ),
    ( 'lena_oxton', 'character:lena "tracer" oxton' ),
    ( 'lenaoxton', 'character:lena "tracer" oxton' ),
    ( 'tracer (character)', 'character:lena "tracer" oxton' ),
    ( 'tracer (cosplay)', 'character:lena "tracer" oxton' ),
    ( 'tracer (lena oxton)', 'character:lena "tracer" oxton' ),
    ( 'tracer (overwatch', 'character:lena "tracer" oxton' ),
    ( 'tracer (overwatch)doll joints', 'character:lena "tracer" oxton' ),
    ( 'tracer overwatch', 'character:lena "tracer" oxton' ),
    ( 'tracer\overwatch', 'character:lena "tracer" oxton' ),
    ( 'tracer_(cosplay)', 'character:lena "tracer" oxton' ),
    ( 'tracer_(overwatch)', 'character:lena "tracer" oxton' ),
    ( 'tracer_(overwatch)_(cosplay)', 'character:lena "tracer" oxton' ),
    ( 'tracer_overwatch', 'character:lena "tracer" oxton' ),
    ( 'トレーサー', 'character:lena "tracer" oxton' ),
    ( 'character:li-ming', 'character:li-ming the rebellious wizard' ),
    ( 'character:li-ming (heroes of the storm)', 'character:li-ming the rebellious wizard' ),
    ( 'li-ming', 'character:li-ming the rebellious wizard' ),
    ( 'li-ming (heroes of the storm)', 'character:li-ming the rebellious wizard' ),
    ( 'character:lucio', 'character:lúcio correia dos santos' ),
    ( 'character:lucio (overwatch) (cosplay)', 'character:lúcio correia dos santos' ),
    ( 'character:lucio correia dos santos', 'character:lúcio correia dos santos' ),
    ( 'character:lúcio correia dos santos (overwatch)', 'character:lúcio correia dos santos' ),
    ( 'character:lúcios', 'character:lúcio correia dos santos' ),
    ( 'hippityhop lucio', 'character:lúcio correia dos santos' ),
    ( 'jazzy lucio', 'character:lúcio correia dos santos' ),
    ( 'lucio correia dos santos', 'character:lúcio correia dos santos' ),
    ( 'lucio overwatch)', 'character:lúcio correia dos santos' ),
    ( 'lucio_(overwatch)', 'character:lúcio correia dos santos' ),
    ( 'lucio_correia_dos_santos', 'character:lúcio correia dos santos' ),
    ( 'lúcio', 'character:lúcio correia dos santos' ),
    ( 'ribbit lucio', 'character:lúcio correia dos santos' ),
    ( 'character:bajie roadhog', 'character:mako "roadhog" rutledge' ),
    ( 'character:junkenstein\'s monster roadhog', 'character:mako "roadhog" rutledge' ),
    ( 'character:junkenstein\'s monster roadhog (overwatch)', 'character:mako "roadhog" rutledge' ),
    ( 'character:mako "roadhog" rutledge (overwatch)', 'character:mako "roadhog" rutledge' ),
    ( 'character:mako rutledge', 'character:mako "roadhog" rutledge' ),
    ( 'character:roadhog (cosplay)', 'character:mako "roadhog" rutledge' ),
    ( 'character:roadhog (overwatch) (cosplay)', 'character:mako "roadhog" rutledge' ),
    ( 'junkenstein\'s monster roadhog', 'character:mako "roadhog" rutledge' ),
    ( 'roadhog (cosplay)', 'character:mako "roadhog" rutledge' ),
    ( 'roadhog (overwatch) (cosplay)', 'character:mako "roadhog" rutledge' ),
    ( 'roadhog_(overwatch)', 'character:mako "roadhog" rutledge' ),
    ( 'roadhog_(overwatch)_(cosplay)', 'character:mako "roadhog" rutledge' ),
    ( 'sharkbait roadhog', 'character:mako "roadhog" rutledge' ),
    ( 'mei (overwatch)', 'character:mei (overwatch)' ),
    ( 'mei (overwatch) (cosplay)', 'character:mei (overwatch)' ),
    ( 'mei overwatch', 'character:mei (overwatch)' ),
    ( 'overwatch mei', 'character:mei (overwatch)' ),
    ( 'character:mei (overwatch)', 'character:mei-ling zhou (overwatch)' ),
    ( 'character:moira', 'character:moira o’deorain' ),
    ( 'character:moira (overwatch)', 'character:moira o’deorain' ),
    ( 'character:moira o\'deorain', 'character:moira o’deorain' ),
    ( 'moira_(overwatch)', 'character:moira o’deorain' ),
    ( 'character:nova (starcraft)', 'character:nova terra' ),
    ( 'nova terra', 'character:nova terra' ),
    ( 'nova terra‎', 'character:nova terra' ),
    ( 'nova_terra', 'character:nova terra' ),
    ( 'character:olivia colomar', 'character:olivia "sombra" colomar' ),
    ( 'character:sombra', 'character:olivia "sombra" colomar' ),
    ( 'character:sombra (overwatch) (cosplay)', 'character:olivia "sombra" colomar' ),
    ( 'character:sombra_(overwatch)', 'character:olivia "sombra" colomar' ),
    ( 'sombra', 'character:olivia "sombra" colomar' ),
    ( 'sombra overwatch', 'character:olivia "sombra" colomar' ),
    ( 'sombra_overwatch', 'character:olivia "sombra" colomar' ),
    ( 'character:sombra (overwatch)', 'character:olivia colomar' ),
    ( 'character:orisa (overwatch)', 'character:orisa' ),
    ( 'orisa (overwatch)', 'character:orisa' ),
    ( 'orisa_(overwatch)', 'character:orisa' ),
    ( 'queen azshara', 'character:queen azshara' ),
    ( 'character:balderich reinhardt', 'character:reinhardt wilhelm' ),
    ( 'character:bundeswehr reinhardt', 'character:reinhardt wilhelm' ),
    ( 'character:bundeswehr reinhardt (overwatch)', 'character:reinhardt wilhelm' ),
    ( 'character:chaos (reinhardt)', 'character:reinhardt wilhelm' ),
    ( 'character:reinhardt', 'character:reinhardt wilhelm' ),
    ( 'character:reinhardt (overwatch) (cosplay)', 'character:reinhardt wilhelm' ),
    ( 'reinhardt (overwatch) (cosplay)', 'character:reinhardt wilhelm' ),
    ( 'reinhardt_(overwatch)', 'character:reinhardt wilhelm' ),
    ( 'reinhardt_(overwatch)_(cosplay)', 'character:reinhardt wilhelm' ),
    ( 'character:reinhardt wilhelm', 'character:reinhardt wilhelm (overwatch)' ),
    ( 'kerrigan', 'character:sarah kerrigan' ),
    ( 'sarah kerrigan', 'character:sarah kerrigan' ),
    ( 'sarah_kerrigan', 'character:sarah kerrigan' ),
    ( 'character:satya "symmetra" vaswani (overwatch)', 'character:satya "symmetra" vaswani' ),
    ( 'character:symmetra (overwatch) (cosplay)', 'character:satya "symmetra" vaswani' ),
    ( 'character:symmetra (ow)', 'character:satya "symmetra" vaswani' ),
    ( 'satya vasmani', 'character:satya "symmetra" vaswani' ),
    ( 'satya_vaswani', 'character:satya "symmetra" vaswani' ),
    ( 'symmetra (cosplay)', 'character:satya "symmetra" vaswani' ),
    ( 'symmetra_(cosplay)', 'character:satya "symmetra" vaswani' ),
    ( 'symmetra_(overwatch)', 'character:satya "symmetra" vaswani' ),
    ( 'symmetra_(overwatch)_(cosplay)', 'character:satya "symmetra" vaswani' ),
    ( 'vaswani', 'character:satya "symmetra" vaswani' ),
    ( 'overwatch sombra', 'character:sombra (overwatch)' ),
    ( 'sombra (overwatch)', 'character:sombra (overwatch)' ),
    ( 'sombra_(overwatch)', 'character:sombra (overwatch)' ),
    ( 'character:sylvanas', 'character:sylvanas windrunner' ),
    ( 'character:sylvanas windrunner (warcraft)', 'character:sylvanas windrunner' ),
    ( 'character:sylvanas_windrunner', 'character:sylvanas windrunner' ),
    ( 'sylvanas', 'character:sylvanas windrunner' ),
    ( 'sylvanas windrunner', 'character:sylvanas windrunner' ),
    ( 'sylvanas_windrunner', 'character:sylvanas windrunner' ),
    ( 'sylvanaswindrunner', 'character:sylvanas windrunner' ),
    ( 'character:sylvanas windrunner', 'character:sylvanas windrunner, the banshee quen' ),
    ( 'character:tekhartha zenyatta (overwatch)', 'character:tekhartha zenyatta' ),
    ( 'character:torbjörn', 'character:torbjörn lindholm' ),
    ( 'character:torbjörn lindholm (overwatch)', 'character:torbjörn lindholm' ),
    ( 'character:torbjörn_lindholm', 'character:torbjörn lindholm' ),
    ( 'torbjorn (overwatch) (cosplay)', 'character:torbjörn lindholm' ),
    ( 'torbjorn_(overwatch)', 'character:torbjörn lindholm' ),
    ( 'torbjörn (overwatch)', 'character:torbjörn lindholm' ),
    ( 'character:tyrande', 'character:tyrande whisperwind' ),
    ( 'character:tyrande_whisperwind', 'character:tyrande whisperwind' ),
    ( 'tyrande', 'character:tyrande whisperwind' ),
    ( 'tyrande whisperwind', 'character:tyrande whisperwind' ),
    ( 'tyrande windwhisper', 'character:tyrande whisperwind' ),
    ( 'tyrande_whisperwind', 'character:tyrande whisperwind' ),
    ( 'tyrandewhisperwind', 'character:tyrande whisperwind' ),
    ( 'bastion_(overwatch)_(cosplay)', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'character:bastion (overwatch)', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'character:bastion (overwatch) (cosplay)', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'character:bastion(overwatch)', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'character:omnic crisis bastion', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'character:overgrown bastion', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'omnic crisis bastion', 'character:“bastion", sst laboratories siege automaton e54' ),
    ( 'copyright:diablo', 'series:diablo' ),
    ( 'diablo', 'series:diablo' ),
    ( 'diablo 2', 'series:diablo ii' ),
    ( 'series:diablo 2', 'series:diablo ii' ),
    ( 'diablo3', 'series:diablo iii' ),
    ( 'diablo 3', 'series:diablo iii' ),
    ( 'series:diablo 3', 'series:diablo iii' ),
    ( 'copyright:overwatch', 'series:overwatch' ),
    ( 'game:overwatch', 'series:overwatch' ),
    ( 'hydrus invalid tag:"series: overwatch"', 'series:overwatch' ),
    ( 'over watch', 'series:overwatch' ),
    ( 'over_watch', 'series:overwatch' ),
    ( 'overlook', 'series:overwatch' ),
    ( 'overwatch', 'series:overwatch' ),
    ( 'parody:overwatch', 'series:overwatch' ),
    ( 'series:invalid subtag " overwatch"', 'series:overwatch' ),
    ( 'オーバーウォッチ', 'series:overwatch' ),
    ( '守望先锋', 'series:overwatch' ),
    ( '오버워치', 'series:overwatch' ),
    ( 'copyright:starcraft', 'series:starcraft' ),
    ( 'starcraft', 'series:starcraft' ),
    ( 'copyright:warcraft', 'series:warcraft' ),
    ( 'warcraft', 'series:warcraft' ),
    ( 'ウォークラフト', 'series:warcraft' ),
    ( 'copyright:world of warcraft', 'series:world of warcraft' ),
    ( 'parody:world of warcraft', 'series:world of warcraft' ),
    ( 'series:world_of_warcraft', 'series:world of warcraft' ),
    ( 'series:wow', 'series:world of warcraft' ),
    ( 'world of warcraft', 'series:world of warcraft' ),
    ( 'world_of_warc', 'series:world of warcraft' ),
    ( 'world_of_warcra', 'series:world of warcraft' ),
    ( 'world_of_warcraf', 'series:world of warcraft' ),
    ( 'world_of_warcraft', 'series:world of warcraft' ),
    ( 'worldofwarcraft', 'series:world of warcraft' ),
    ( 'character:night elf', 'species:night elf' ),
    ( 'character:night_elf', 'species:night elf' ),
    ( 'night elf', 'species:night elf' ),
    ( 'nightelf', 'species:night elf' ),
    ( 'species:nightelf', 'species:night elf' ),
    ( 'black tauren', 'species:tauren' ),
    ( 'character:tauren', 'species:tauren' ),
    ( 'tauren', 'species:tauren' ),
    ( 'tauren druid', 'species:tauren' ),
    ( 'taurens', 'species:tauren' ),
    ( 'blizzard (company)', 'studio:blizzard entertainment' ),
    ( 'blizzard entertainment', 'studio:blizzard entertainment' ),
    ( 'blizzard_(company)', 'studio:blizzard entertainment' ),
    ( 'blizzard_entertainment', 'studio:blizzard entertainment' ),
    ( 'circle:blizzard entertainment', 'studio:blizzard entertainment' ),
    ( 'copyright:blizzard entertainment', 'studio:blizzard entertainment' ),
    ( 'creator:blizzard entertainment', 'studio:blizzard entertainment' ),
    ( 'idol:blizzard entertainment', 'studio:blizzard entertainment' ),
    ( 'series:blizzard (company)', 'studio:blizzard entertainment' ),
    ( 'series:blizzard entertainment', 'studio:blizzard entertainment' ),
    ( 'studio:ブリザードエンターテインメント', 'studio:blizzard entertainment' )
}

class TestClientDBTags( unittest.TestCase ):
    
    @classmethod
    def _create_db( cls ):
        
        # class variable
        cls._db = ClientDB.DB( HG.test_controller, TestController.DB_DIR, 'client' )
        
        HG.test_controller.SetRead( 'hash_status', ( CC.STATUS_UNKNOWN, None, '' ) )
        
    
    @classmethod
    def _delete_db( cls ):
        
        cls._db.Shutdown()
        
        while not cls._db.LoopIsFinished():
            
            time.sleep( 0.1 )
            
        
        db_filenames = list(cls._db._db_filenames.values())
        
        for filename in db_filenames:
            
            path = os.path.join( TestController.DB_DIR, filename )
            
            os.remove( path )
            
        
        del cls._db
        
    
    @classmethod
    def setUpClass( cls ):
        
        cls._db = ClientDB.DB( HG.test_controller, TestController.DB_DIR, 'client' )
        
        HG.test_controller.SetRead( 'hash_status', ( CC.STATUS_UNKNOWN, None, '' ) )
        
    
    @classmethod
    def tearDownClass( cls ):
        
        cls._delete_db()
        
    
    def _read( self, action, *args, **kwargs ): return TestClientDBTags._db.Read( action, *args, **kwargs )
    def _write( self, action, *args, **kwargs ): return TestClientDBTags._db.Write( action, True, *args, **kwargs )
    
    def _clear_db( self ):
        
        TestClientDBTags._delete_db()
        
        TestClientDBTags._create_db()
        
        #
        
        services = self._read( 'services' )
        
        self._my_service_key = HydrusData.GenerateKey()
        self._processing_service_key = HydrusData.GenerateKey()
        self._public_service_key = HydrusData.GenerateKey()
        
        services.append( ClientServices.GenerateService( self._my_service_key, HC.LOCAL_TAG, 'personal tags' ) )
        services.append( ClientServices.GenerateService( self._processing_service_key, HC.LOCAL_TAG, 'processing tags' ) )
        services.append( ClientServices.GenerateService( self._public_service_key, HC.TAG_REPOSITORY, 'public tags' ) )
        
        self._write( 'update_services', services )
        
        #
        
        self._samus_bad = bytes.fromhex( '5d884d84813beeebd59a35e474fa3e4742d0f2b6679faa7609b245ddbbd05444' )
        self._samus_both = bytes.fromhex( 'cdc67d3b377e6e1397ffa55edc5b50f6bdf4482c7a6102c6f27fa351429d6f49' )
        self._samus_good = bytes.fromhex( '9e7b8b5abc7cb11da32db05671ce926a2a2b701415d1b2cb77a28deea51010c3' )
        
        self._hashes = { self._samus_bad, self._samus_both, self._samus_good }
        
        media_results = self._read( 'media_results', self._hashes )
        
        for media_result in media_results:
            
            if media_result.GetHash() == self._samus_bad:
                
                self._samus_bad_hash_id = media_result.GetHashId()
                
            elif media_result.GetHash() == self._samus_both:
                
                self._samus_both_hash_id = media_result.GetHashId()
                
            elif media_result.GetHash() == self._samus_good:
                
                self._samus_good_hash_id = media_result.GetHashId()
                
            
        
        self._hash_ids = ( self._samus_bad_hash_id, self._samus_both_hash_id, self._samus_good_hash_id )
        
    
    def _sync_display( self ):
        
        for service_key in ( self._my_service_key, self._processing_service_key, self._public_service_key ):
            
            still_work_to_do = True
            
            while still_work_to_do:
                
                still_work_to_do = self._write( 'sync_tag_display_maintenance', service_key, 1 )
                
            
        
    
    def test_display_pairs_lookup_web_parents( self ):
        
        self._clear_db()
        
        # test empty
        
        self.assertEqual( self._read( 'tag_parents', self._my_service_key ), {} )
        self.assertEqual( self._read( 'tag_siblings', self._my_service_key ), {} )
        
        # tricky situation, we have a parent that is not siblinged
        
        content_updates_1 = []
        content_updates_2 = []
        content_updates_3 = []
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'samus aran', 'metroid' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'samus bodysuit', 'bodysuit' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'samus bodysuit', 'samus aran' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'bodysuit', 'clothing:bodysuit' ) ) )
        
        # this last one should trigger a full on chain regen and rebuild the bodysuit pairs, despite not caring directly about them--does it?
        content_updates_3.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'metroid', 'nintendo' ) ) )
        
        self._write( 'content_updates', { self._my_service_key : content_updates_1 } )
        self._write( 'content_updates', { self._my_service_key : content_updates_2 } )
        self._write( 'content_updates', { self._my_service_key : content_updates_3 } )
        
        self._sync_display()
        
        #
        
        self.assertEqual( self._read( 'tag_siblings_and_parents_lookup', ( 'bodysuit', ) )[ 'bodysuit' ][ self._my_service_key ], ( {
            'bodysuit',
            'clothing:bodysuit'
            }, 'clothing:bodysuit', {
                'samus bodysuit'
            }, set() ) )
        
    
    def test_display_pairs_lookup_tricky( self ):
        
        self._clear_db()
        
        # test empty
        
        self.assertEqual( self._read( 'tag_parents', self._my_service_key ), {} )
        self.assertEqual( self._read( 'tag_siblings', self._my_service_key ), {} )
        
        # tricky situation, we have a parent that is not siblinged
        
        content_updates_1 = []
        content_updates_2 = []
        content_updates_3 = []
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'samus aran', 'metroid' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'series:metroid', 'studio:nintendo' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'samus aran armour', 'character:samus aran' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'metroid', 'series:metroid' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'samus aran', 'character:samus aran' ) ) )
        
        # this last one should trigger a full on chain regen including the difficult to find link--do we find that link on regenning?
        content_updates_3.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'studio:nintendo', 'game studio' ) ) )
        
        self._write( 'content_updates', { self._my_service_key : content_updates_1 } )
        self._write( 'content_updates', { self._my_service_key : content_updates_2 } )
        self._write( 'content_updates', { self._my_service_key : content_updates_3 } )
        
        self._sync_display()
        
        #
        
        self.assertEqual( self._read( 'tag_siblings_and_parents_lookup', ( 'samus aran', ) )[ 'samus aran' ][ self._my_service_key ], ( {
            'character:samus aran',
            'samus aran'
            }, 'character:samus aran', {
                'samus aran armour'
            }, {
            'series:metroid',
            'studio:nintendo',
            'game studio'
            } ) )
        
    
    def test_display_pairs_lookup_bonkers( self ):
        
        self._clear_db()
        
        # test empty
        
        self.assertEqual( self._read( 'tag_parents', self._my_service_key ), {} )
        self.assertEqual( self._read( 'tag_siblings', self._my_service_key ), {} )
        
        #
        
        content_updates_list = [ [] for i in range( 4 ) ]
        
        for pair in IRL_PARENT_PAIRS:
            
            content_updates_list[ random.randint( 1, 3 ) ].append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, pair ) )
            
        
        for pair in IRL_SIBLING_PAIRS:
            
            i = 2
            
            while i == 3:
                
                i = random.randint( 0, 4 )
                
            
            content_updates_list[ i ].append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, pair ) )
            
        
        for content_updates in content_updates_list:
            
            service_keys_to_content_updates_1 = { self._my_service_key : content_updates }
            
            self._write( 'content_updates', service_keys_to_content_updates_1 )
            
        
        self._sync_display()
        
        #
        
        result = self._read( 'tag_parents', self._my_service_key )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_CURRENT ] ), IRL_PARENT_PAIRS )
        
        result = self._read( 'tag_siblings', self._my_service_key )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_CURRENT ] ), IRL_SIBLING_PAIRS )
        
        #
        
        self.assertEqual( self._read( 'tag_siblings_and_parents_lookup', ( 'pharah', ) )[ 'pharah' ][ self._my_service_key ], ( {
            'character:fareeha "pharah" amari',
            'character:fareeha "pharah" amari (overwatch)',
            'character:pharah',
            'character:pharah (ow)',
            'character:pharah_(overwatch)',
            'overwatch pharah',
            'pharah',
            'pharah amari',
            'pharah overwatch',
            'pharah_(overwatch)',
            'pharah_amari'
            }, 'character:fareeha "pharah" amari', set(), {
            'series:overwatch',
            'studio:blizzard entertainment'
            } ) )
        
        self.assertEqual( self._read( 'tag_siblings_and_parents_lookup', ( 'warcraft', ) )[ 'warcraft' ][ self._my_service_key ], ( {
            'series:warcraft',
            'copyright:warcraft',
            'warcraft',
            'ウォークラフト'
            }, 'series:warcraft', {
            'series:world of warcraft',
            'character:tyrande whisperwind',
            'character:alleria windrunner',
            'character:eonar, the life binder',
            'species:tauren',
            'character:queen azshara',
            'character:alextrasza the life-binder',
            'character:lady liadrin',
            'species:night elf',
            'character:jaina proudmoore',
            'character:sylvanas windrunner, the banshee quen'
            }, {
                'studio:blizzard entertainment'
            } ) )
        
    
    def test_parents_pairs_lookup( self ):
        
        self._clear_db()
        
        # test empty
        
        self.assertEqual( self._read( 'tag_parents', self._my_service_key ), {} )
        self.assertEqual( self._read( 'tag_parents', self._public_service_key ), {} )
        
        # now add some structures, a mixture of add and pend in two parts
        
        service_keys_to_content_updates_1 = {}
        service_keys_to_content_updates_2 = {}
        
        content_updates_1 = []
        content_updates_2 = []
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'samus aran', 'cute blonde' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'elf princess', 'cute blonde' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'cute blonde', 'cute' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'cute blonde', 'blonde' ) ) )
        
        service_keys_to_content_updates_1[ self._my_service_key ] = content_updates_1
        service_keys_to_content_updates_2[ self._my_service_key ] = content_updates_2
        
        content_updates_1 = []
        content_updates_2 = []
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'bodysuit', 'nice clothing' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'bikini', 'nice clothing' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'nice clothing', 'nice' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'nice clothing', 'clothing' ) ) )
        
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'metroid', 'sci-fi' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'star trek', 'sci-fi' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'sci-fi', 'sci' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'sci-fi', 'fi' ) ) )
        
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'splashbrush', 'an artist' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'incase', 'an artist' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'an artist', 'an' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'an artist', 'artist' ) ) )
        
        service_keys_to_content_updates_1[ self._public_service_key ] = content_updates_1
        service_keys_to_content_updates_2[ self._public_service_key ] = content_updates_2
        
        self._write( 'content_updates', service_keys_to_content_updates_1 )
        self._write( 'content_updates', service_keys_to_content_updates_2 )
        
        self._sync_display()
        
        # were pairs all added right?
        
        result = self._read( 'tag_parents', self._my_service_key )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_CURRENT ] ), {
            ( 'samus aran', 'cute blonde' ),
            ( 'elf princess', 'cute blonde' ),
            ( 'cute blonde', 'cute' ),
            ( 'cute blonde', 'blonde' )
        } )
        
        result = self._read( 'tag_parents', self._public_service_key )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_CURRENT ] ), {
            ( 'bodysuit', 'nice clothing' ),
            ( 'bikini', 'nice clothing' ),
            ( 'nice clothing', 'nice' ),
            ( 'nice clothing', 'clothing' ),
            ( 'splashbrush', 'an artist' ),
            ( 'an artist', 'an')
        } )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_PENDING ] ), {
            ( 'metroid', 'sci-fi' ),
            ( 'star trek', 'sci-fi' ),
            ( 'sci-fi', 'sci' ),
            ( 'sci-fi', 'fi' ),
            ( 'incase', 'an artist' ),
            ( 'an artist', 'artist' )
        } )
        
        # are lookups working right?
        
        all_tags = {
            'samus aran',
            'elf princess',
            'cute blonde',
            'cute',
            'blonde'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for ( tag, expected_descendants, expected_ancestors ) in (
            (
                'samus aran',
                set(),
                { 'cute blonde', 'cute', 'blonde' }
            ),
            (
                'elf princess',
                set(),
                { 'cute blonde', 'cute', 'blonde' }
            ),
            (
                'cute blonde',
                { 'samus aran', 'elf princess' },
                { 'cute', 'blonde' }
            ),
            (
                'cute',
                { 'cute blonde', 'samus aran', 'elf princess' },
                set()
            ),
            (
                'blonde',
                { 'cute blonde', 'samus aran', 'elf princess' },
                set()
            )
        ):
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._my_service_key ]
            
            self.assertEqual( sibling_chain_members, { tag } )
            
            self.assertEqual( ideal_tag, tag )
            self.assertEqual( descendants, expected_descendants )
            self.assertEqual( ancestors, expected_ancestors )
            
        
        all_tags = {
            'bodysuit',
            'bikini',
            'nice clothing',
            'nice',
            'clothing',
            'metroid',
            'star trek',
            'sci-fi',
            'sci',
            'fi',
            'splashbrush',
            'incase',
            'an artist',
            'an',
            'artist'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for ( tag, expected_descendants, expected_ancestors ) in (
            (
                'bodysuit',
                set(),
                { 'nice clothing', 'nice', 'clothing' }
            ),
            (
                'bikini',
                set(),
                { 'nice clothing', 'nice', 'clothing' }
            ),
            (
                'nice clothing',
                { 'bodysuit', 'bikini' },
                { 'nice', 'clothing' }
            ),
            (
                'nice',
                { 'nice clothing', 'bodysuit', 'bikini' },
                set()
            ),
            (
                'clothing',
                { 'nice clothing', 'bodysuit', 'bikini' },
                set()
            ),
            (
                'metroid',
                set(),
                { 'sci-fi', 'sci', 'fi' }
            ),
            (
                'star trek',
                set(),
                { 'sci-fi', 'sci', 'fi' }
            ),
            (
                'sci-fi',
                { 'metroid', 'star trek' },
                { 'sci', 'fi' }
            ),
            (
                'sci',
                { 'sci-fi', 'metroid', 'star trek' },
                set()
            ),
            (
                'fi',
                { 'sci-fi', 'metroid', 'star trek' },
                set()
            ),
            (
                'splashbrush',
                set(),
                { 'an artist', 'an', 'artist' }
            ),
            (
                'incase',
                set(),
                { 'an artist', 'an', 'artist' }
            ),
            (
                'an artist',
                { 'splashbrush', 'incase' },
                { 'an', 'artist' }
            ),
            (
                'an',
                { 'an artist', 'splashbrush', 'incase' },
                set()
            ),
            (
                'artist',
                { 'an artist', 'splashbrush', 'incase' },
                set()
            )
        ):
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._public_service_key ]
            
            self.assertEqual( sibling_chain_members, { tag } )
            
            self.assertEqual( ideal_tag, tag )
            self.assertEqual( descendants, expected_descendants )
            self.assertEqual( ancestors, expected_ancestors )
            
        
        # add some bad parents
        
        service_keys_to_content_updates = {}
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'lara croft', 'cute blonde' ) ) )
        
        service_keys_to_content_updates[ self._my_service_key ] = content_updates
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_ADD, ( 'dirty rags', 'nice clothing' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'lotr', 'sci-fi' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_PEND, ( 'myself', 'an artist' ) ) )
        
        service_keys_to_content_updates[ self._public_service_key ] = content_updates
        
        self._write( 'content_updates', service_keys_to_content_updates )
        
        self._sync_display()
        
        # added right?
        
        all_tags = {
            'lara croft'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for ( tag, expected_descendants, expected_ancestors ) in (
            (
                'lara croft',
                set(),
                { 'cute blonde', 'cute', 'blonde' }
            ),
        ):
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._my_service_key ]
            
            self.assertEqual( sibling_chain_members, { tag } )
            
            self.assertEqual( ideal_tag, tag )
            self.assertEqual( descendants, expected_descendants )
            self.assertEqual( ancestors, expected_ancestors )
            
        
        all_tags = {
            'dirty rags',
            'lotr',
            'myself'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for ( tag, expected_descendants, expected_ancestors ) in (
            (
                'dirty rags',
                set(),
                { 'nice clothing', 'nice', 'clothing' }
            ),
            (
                'lotr',
                set(),
                { 'sci-fi', 'sci', 'fi' }
            ),
            (
                'myself',
                set(),
                { 'an artist', 'an', 'artist' }
            )
        ):
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._public_service_key ]
            
            self.assertEqual( sibling_chain_members, { tag } )
            
            self.assertEqual( ideal_tag, tag )
            self.assertEqual( descendants, expected_descendants )
            self.assertEqual( ancestors, expected_ancestors )
            
        
        # now remove them
        
        service_keys_to_content_updates = {}
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_DELETE, ( 'lara croft', 'cute blonde' ) ) )
        
        service_keys_to_content_updates[ self._my_service_key ] = content_updates
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_DELETE, ( 'dirty rags', 'nice clothing' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_RESCIND_PEND, ( 'lotr', 'sci-fi' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_PARENTS, HC.CONTENT_UPDATE_RESCIND_PEND, ( 'myself', 'an artist' ) ) )
        
        service_keys_to_content_updates[ self._public_service_key ] = content_updates
        
        self._write( 'content_updates', service_keys_to_content_updates )
        
        self._sync_display()
        
        # and they went, right?
        
        all_tags = {
            'samus aran',
            'elf princess',
            'cute blonde',
            'cute',
            'blonde',
            'lara croft'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for ( tag, expected_descendants, expected_ancestors ) in (
            (
                'samus aran',
                set(),
                { 'cute blonde', 'cute', 'blonde' }
            ),
            (
                'elf princess',
                set(),
                { 'cute blonde', 'cute', 'blonde' }
            ),
            (
                'cute blonde',
                { 'samus aran', 'elf princess' },
                { 'cute', 'blonde' }
            ),
            (
                'cute',
                { 'cute blonde', 'samus aran', 'elf princess' },
                set()
            ),
            (
                'blonde',
                { 'cute blonde', 'samus aran', 'elf princess' },
                set()
            ),
            (
                'lara croft',
                set(),
                set()
            )
        ):
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._my_service_key ]
            
            self.assertEqual( sibling_chain_members, { tag } )
            
            self.assertEqual( ideal_tag, tag )
            self.assertEqual( descendants, expected_descendants )
            self.assertEqual( ancestors, expected_ancestors )
            
        
        all_tags = {
            'bodysuit',
            'bikini',
            'nice clothing',
            'nice',
            'clothing',
            'metroid',
            'star trek',
            'sci-fi',
            'sci',
            'fi',
            'splashbrush',
            'incase',
            'an artist',
            'an',
            'artist',
            'dirty rags',
            'lotr',
            'myself'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for ( tag, expected_descendants, expected_ancestors ) in (
            (
                'bodysuit',
                set(),
                { 'nice clothing', 'nice', 'clothing' }
            ),
            (
                'bikini',
                set(),
                { 'nice clothing', 'nice', 'clothing' }
            ),
            (
                'nice clothing',
                { 'bodysuit', 'bikini' },
                { 'nice', 'clothing' }
            ),
            (
                'nice',
                { 'nice clothing', 'bodysuit', 'bikini' },
                set()
            ),
            (
                'clothing',
                { 'nice clothing', 'bodysuit', 'bikini' },
                set()
            ),
            (
                'metroid',
                set(),
                { 'sci-fi', 'sci', 'fi' }
            ),
            (
                'star trek',
                set(),
                { 'sci-fi', 'sci', 'fi' }
            ),
            (
                'sci-fi',
                { 'metroid', 'star trek' },
                { 'sci', 'fi' }
            ),
            (
                'sci',
                { 'sci-fi', 'metroid', 'star trek' },
                set()
            ),
            (
                'fi',
                { 'sci-fi', 'metroid', 'star trek' },
                set()
            ),
            (
                'splashbrush',
                set(),
                { 'an artist', 'an', 'artist' }
            ),
            (
                'incase',
                set(),
                { 'an artist', 'an', 'artist' }
            ),
            (
                'an artist',
                { 'splashbrush', 'incase' },
                { 'an', 'artist' }
            ),
            (
                'an',
                { 'an artist', 'splashbrush', 'incase' },
                set()
            ),
            (
                'artist',
                { 'an artist', 'splashbrush', 'incase' },
                set()
            ),
            (
                'dirty rags',
                set(),
                set()
            ),
            (
                'lotr',
                set(),
                set()
            ),
            (
                'myself',
                set(),
                set()
            )
        ):
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._public_service_key ]
            
            self.assertEqual( sibling_chain_members, { tag } )
            
            self.assertEqual( ideal_tag, tag )
            self.assertEqual( descendants, expected_descendants )
            self.assertEqual( ancestors, expected_ancestors )
            
        
    
    def test_siblings_pairs_lookup( self ):
        
        self._clear_db()
        
        # test empty
        
        self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
        self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
        
        # now add some structures, a mixture of add and pend in two parts
        
        service_keys_to_content_updates_1 = {}
        service_keys_to_content_updates_2 = {}
        
        content_updates_1 = []
        content_updates_2 = []
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'sameus aran', 'samus aran' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'samus_aran_(character)', 'character:samus aran' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'samus aran', 'character:samus aran' ) ) )
        
        service_keys_to_content_updates_1[ self._my_service_key ] = content_updates_1
        service_keys_to_content_updates_2[ self._my_service_key ] = content_updates_2
        
        content_updates_1 = []
        content_updates_2 = []
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'bodysut', 'bodysuit' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'bodysuit_(clothing)', 'clothing:bodysuit' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'bodysuit', 'clothing:bodysuit' ) ) )
        
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PEND, ( 'metrod', 'metroid' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PEND, ( 'metroid_(series)', 'series:metroid' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PEND, ( 'metroid', 'series:metroid' ) ) )
        
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'splashbush', 'splashbrush' ) ) )
        content_updates_2.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'splashbrush_(artist)', 'creator:splashbrush' ) ) )
        content_updates_1.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PEND, ( 'splashbrush', 'creator:splashbrush' ) ) )
        
        service_keys_to_content_updates_1[ self._public_service_key ] = content_updates_1
        service_keys_to_content_updates_2[ self._public_service_key ] = content_updates_2
        
        self._write( 'content_updates', service_keys_to_content_updates_1 )
        self._write( 'content_updates', service_keys_to_content_updates_2 )
        
        self._sync_display()
        
        # were pairs all added right?
        
        result = self._read( 'tag_siblings', self._my_service_key )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_CURRENT ] ), {
            ( 'sameus aran', 'samus aran' ),
            ( 'samus_aran_(character)', 'character:samus aran' ),
            ( 'samus aran', 'character:samus aran' )
        } )
        
        result = self._read( 'tag_siblings', self._public_service_key )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_CURRENT ] ), {
            ( 'bodysut', 'bodysuit' ),
            ( 'bodysuit_(clothing)', 'clothing:bodysuit' ),
            ( 'bodysuit', 'clothing:bodysuit' ),
            ( 'splashbush', 'splashbrush' ),
            ( 'splashbrush_(artist)', 'creator:splashbrush' )
        } )
        
        self.assertEqual( set( result[ HC.CONTENT_STATUS_PENDING ] ), {
            ( 'metrod', 'metroid' ),
            ( 'metroid_(series)', 'series:metroid' ),
            ( 'metroid', 'series:metroid' ),
            ( 'splashbrush', 'creator:splashbrush' )
        } )
        
        # did they get constructed correctly?
        
        self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {
            'sameus aran' : 'character:samus aran',
            'samus_aran_(character)' : 'character:samus aran',
            'samus aran' : 'character:samus aran'
        } )
        
        self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {
            'bodysut' : 'clothing:bodysuit',
            'bodysuit_(clothing)' : 'clothing:bodysuit',
            'bodysuit' : 'clothing:bodysuit',
            'metrod' : 'series:metroid',
            'metroid_(series)' : 'series:metroid',
            'metroid' : 'series:metroid',
            'splashbush' : 'creator:splashbrush',
            'splashbrush_(artist)' : 'creator:splashbrush',
            'splashbrush' : 'creator:splashbrush'
        } )
        
        # are lookups working right?
        
        all_tags = {
            'sameus aran',
            'samus aran',
            'samus_aran_(character)',
            'character:samus aran'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for tag in {
            'sameus aran',
            'samus aran',
            'samus_aran_(character)',
            'character:samus aran'
        }:
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._my_service_key ]
            
            self.assertEqual( sibling_chain_members, {
                'sameus aran',
                'samus aran',
                'samus_aran_(character)',
                'character:samus aran'
            } )
            
            self.assertEqual( ideal_tag, 'character:samus aran' )
            self.assertEqual( descendants, set() )
            self.assertEqual( ancestors, set() )
            
        
        all_tags = {
            'bodysut',
            'bodysuit_(clothing)',
            'bodysuit',
            'clothing:bodysuit',
            'metrod',
            'metroid_(series)',
            'metroid',
            'series:metroid',
            'splashbush',
            'splashbrush_(artist)',
            'splashbrush',
            'creator:splashbrush'
        }
        
        selected_tag_to_service_keys_to_siblings_and_parents = self._read( 'tag_siblings_and_parents_lookup', all_tags )
        
        for tag in {
            'bodysut',
            'bodysuit_(clothing)',
            'bodysuit',
            'clothing:bodysuit',
        }:
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._public_service_key ]
            
            self.assertEqual( sibling_chain_members, {
                'bodysut',
                'bodysuit_(clothing)',
                'bodysuit',
                'clothing:bodysuit',
            } )
            
            self.assertEqual( ideal_tag, 'clothing:bodysuit' )
            self.assertEqual( descendants, set() )
            self.assertEqual( ancestors, set() )
            
        
        for tag in {
            'metrod',
            'metroid_(series)',
            'metroid',
            'series:metroid',
        }:
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._public_service_key ]
            
            self.assertEqual( sibling_chain_members, {
                'metrod',
                'metroid_(series)',
                'metroid',
                'series:metroid',
            } )
            
            self.assertEqual( ideal_tag, 'series:metroid' )
            self.assertEqual( descendants, set() )
            self.assertEqual( ancestors, set() )
            
        
        for tag in {
            'splashbush',
            'splashbrush_(artist)',
            'splashbrush',
            'creator:splashbrush'
        }:
            
            ( sibling_chain_members, ideal_tag, descendants, ancestors ) = selected_tag_to_service_keys_to_siblings_and_parents[ tag ][ self._public_service_key ]
            
            self.assertEqual( sibling_chain_members, {
                'splashbush',
                'splashbrush_(artist)',
                'splashbrush',
                'creator:splashbrush'
            } )
            
            self.assertEqual( ideal_tag, 'creator:splashbrush' )
            self.assertEqual( descendants, set() )
            self.assertEqual( ancestors, set() )
            
        
        # add some bad siblings
        
        service_keys_to_content_updates = {}
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'lara croft', 'character:samus aran' ) ) )
        
        service_keys_to_content_updates[ self._my_service_key ] = content_updates
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'shorts', 'clothing:bodysuit' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PEND, ( 'tomb raider', 'series:metroid' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PEND, ( 'incase', 'creator:splashbrush' ) ) )
        
        service_keys_to_content_updates[ self._public_service_key ] = content_updates
        
        self._write( 'content_updates', service_keys_to_content_updates )
        
        self._sync_display()
        
        # added right?
        
        result = self._read( 'tag_siblings_all_ideals', self._my_service_key )
        
        self.assertIn( 'lara croft', result )
        self.assertEqual( result[ 'lara croft' ], 'character:samus aran' )
        
        result = self._read( 'tag_siblings_all_ideals', self._public_service_key )
        
        self.assertIn( 'shorts', result )
        self.assertIn( 'tomb raider', result )
        self.assertIn( 'incase', result )
        self.assertEqual( result[ 'shorts' ], 'clothing:bodysuit' )
        self.assertEqual( result[ 'tomb raider' ], 'series:metroid' )
        self.assertEqual( result[ 'incase' ], 'creator:splashbrush' )
        
        # now remove them
        
        service_keys_to_content_updates = {}
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'lara croft', 'character:samus aran' ) ) )
        
        service_keys_to_content_updates[ self._my_service_key ] = content_updates
        
        content_updates = []
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'shorts', 'clothing:bodysuit' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_RESCIND_PEND, ( 'tomb raider', 'series:metroid' ) ) )
        
        content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_RESCIND_PEND, ( 'incase', 'creator:splashbrush' ) ) )
        
        service_keys_to_content_updates[ self._public_service_key ] = content_updates
        
        self._write( 'content_updates', service_keys_to_content_updates )
        
        self._sync_display()
        
        # and they went, right?
        
        self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {
            'sameus aran' : 'character:samus aran',
            'samus_aran_(character)' : 'character:samus aran',
            'samus aran' : 'character:samus aran'
        } )
        
        self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {
            'bodysut' : 'clothing:bodysuit',
            'bodysuit_(clothing)' : 'clothing:bodysuit',
            'bodysuit' : 'clothing:bodysuit',
            'metrod' : 'series:metroid',
            'metroid_(series)' : 'series:metroid',
            'metroid' : 'series:metroid',
            'splashbush' : 'creator:splashbrush',
            'splashbrush_(artist)' : 'creator:splashbrush',
            'splashbrush' : 'creator:splashbrush'
        } )
        
    
    def test_siblings_application_lookup( self ):
        
        # three complicated lads that differ
        
        # test none
        # test one
        # test one from another service
        # test three
        # change order
        
        pass
        
    
    def test_siblings_application_autocomplete_counts( self ):
        
        # test none
        # test one
        # test one from another service
        # test three
        # change order
        
        pass
        
    
    def test_siblings_application_autocomplete_search( self ):
        
        # test none
        # test one
        # test one from another service
        # test three
        # change order
        
        pass
        
    
    def test_siblings_files_tag_autocomplete_counts_specific( self ):
        
        # set up some siblings
        # add file
        # remove file
        
        pass
        
    
    def test_siblings_files_tags_combined( self ):
        
        # set up some siblings
        # add file
        # remove file
        
        pass
        
    
    def test_siblings_files_tags_specific( self ):
        
        # set up some siblings
        # add file
        # remove file
        
        # do on a file in a specific domain and not in
        
        pass
        
    
    def test_siblings_tags_combined( self ):
        
        # set up some siblings
        
        # add/delete
        # pend/petition
        
        pass
        
    
    def test_siblings_tags_specific( self ):
        
        # set up some siblings
        
        # add/delete
        # pend/petition
        
        # do on a file in a specific domain and not in
        
        pass
        
    
    def test_tag_siblings( self ):
        
        # this sucks big time and should really be broken into specific scenarios to test add_file with tags and sibs etc...
        
        def test_ac( search_text, tag_service_key, file_service_key, expected_storage_tags_to_counts, expected_display_tags_to_counts ):
            
            tag_search_context = ClientSearch.TagSearchContext( tag_service_key )
            
            preds = self._read( 'autocomplete_predicates', ClientTags.TAG_DISPLAY_STORAGE, tag_search_context, file_service_key, search_text = search_text )
            
            tags_to_counts = { pred.GetValue() : pred.GetAllCounts() for pred in preds }
            
            self.assertEqual( expected_storage_tags_to_counts, tags_to_counts )
            
            preds = self._read( 'autocomplete_predicates', ClientTags.TAG_DISPLAY_ACTUAL, tag_search_context, file_service_key, search_text = search_text )
            
            tags_to_counts = { pred.GetValue() : pred.GetAllCounts() for pred in preds }
            
            self.assertEqual( expected_display_tags_to_counts, tags_to_counts )
            
        
        for on_local_files in ( False, True ):
            
            def test_no_sibs( force_no_local_files = False ):
                
                for do_regen_sibs in ( False, True ):
                    
                    if do_regen_sibs:
                        
                        self._write( 'regenerate_tag_siblings_cache' )
                        
                        self._sync_display()
                        
                    
                    for do_regen_display in ( False, True ):
                        
                        if do_regen_display:
                            
                            self._write( 'regenerate_tag_display_mappings_cache' )
                            
                            self._sync_display()
                            
                        
                        hash_ids_to_tags_managers = self._read( 'force_refresh_tags_managers', self._hash_ids )
                        
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc bad', 'sameus aran' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc bad' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp bad' } )
                        
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc bad', 'sameus aran', 'process these', 'pc bad', 'pp bad' } )
                        
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc bad', 'mc good' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc bad', 'pc good', 'samus metroid' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp bad', 'pp good' } )
                        
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc bad', 'mc good', 'process these', 'pc bad', 'pc good', 'samus metroid', 'pp bad', 'pp good' } )
                        
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good' } )
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good', 'character:samus aran' } )
                        
                        self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'process these', 'pc good', 'pp good', 'character:samus aran' } )
                        
                        test_ac( 'mc bad*', self._my_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ) }, { 'mc bad' : ( 2, None, 0, None ) } )
                        test_ac( 'pc bad*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ) }, { 'pc bad' : ( 2, None, 0, None ) } )
                        test_ac( 'pp bad*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ) }, { 'pp bad' : ( 0, None, 2, None ) } )
                        test_ac( 'sameus aran*', self._my_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'sameus aran' : ( 1, None, 0, None ) } )
                        test_ac( 'samus metroid*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ) }, { 'samus metroid' : ( 1, None, 0, None ) } )
                        test_ac( 'samus aran*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 0, None, 1, None ) } )
                        
                        if on_local_files and not force_no_local_files:
                            
                            test_ac( 'mc bad*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ) }, { 'mc bad' : ( 2, None, 0, None ) } )
                            test_ac( 'pc bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ) }, { 'pc bad' : ( 2, None, 0, None ) } )
                            test_ac( 'pp bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ) }, { 'pp bad' : ( 0, None, 2, None ) } )
                            test_ac( 'sameus aran*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'sameus aran' : ( 1, None, 0, None ) } )
                            test_ac( 'samus metroid*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ) }, { 'samus metroid' : ( 1, None, 0, None ) } )
                            test_ac( 'samus aran*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 0, None, 1, None ) } )
                            
                            test_ac( 'mc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ) }, { 'mc bad' : ( 2, None, 0, None ) } )
                            test_ac( 'pc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ) }, { 'pc bad' : ( 2, None, 0, None ) } )
                            test_ac( 'pp bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ) }, { 'pp bad' : ( 0, None, 2, None ) } )
                            test_ac( 'sameus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'sameus aran' : ( 1, None, 0, None ) } )
                            test_ac( 'samus metroid*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ) }, { 'samus metroid' : ( 1, None, 0, None ) } )
                            test_ac( 'samus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 0, None, 1, None ) } )
                            
                        else:
                            
                            test_ac( 'mc bad*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'pc bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'pp bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'sameus aran*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'samus metroid*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'samus aran*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            
                            test_ac( 'mc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'pc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'pp bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'sameus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'samus metroid*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            test_ac( 'samus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                            
                        
                    
                
            
            self._clear_db()
            
            service_keys_to_content_updates = {}
            
            content_updates = []
            
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_bad, ) ) ) for tag in ( 'mc bad', 'sameus aran' ) ) )
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_both, ) ) ) for tag in ( 'mc bad', 'mc good', ) ) )
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_good, ) ) ) for tag in ( 'mc good', ) ) )
            
            service_keys_to_content_updates[ self._my_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_bad, self._samus_both, self._samus_good ) ) ) for tag in ( 'process these', ) ) )
            
            service_keys_to_content_updates[ self._processing_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_bad, ) ) ) for tag in ( 'pc bad', ) ) )
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_both, ) ) ) for tag in ( 'pc bad', 'pc good', 'samus metroid' ) ) )
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_ADD, ( tag, ( self._samus_good, ) ) ) for tag in ( 'pc good', ) ) )
            
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_PEND, ( tag, ( self._samus_bad, ) ) ) for tag in ( 'pp bad', ) ) )
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_PEND, ( tag, ( self._samus_both, ) ) ) for tag in ( 'pp bad', 'pp good' ) ) )
            content_updates.extend( ( HydrusData.ContentUpdate( HC.CONTENT_TYPE_MAPPINGS, HC.CONTENT_UPDATE_PEND, ( tag, ( self._samus_good, ) ) ) for tag in ( 'pp good', 'character:samus aran' ) ) )
            
            service_keys_to_content_updates[ self._public_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            # start out, no sibs
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            test_no_sibs( force_no_local_files = True )
            
            if on_local_files:
                
                # doing this again tests a very simple add_file
                
                for filename in ( 'muh_jpg.jpg', 'muh_png.png', 'muh_apng.png' ):
                    
                    path = os.path.join( HC.STATIC_DIR, 'testing', filename )
                    
                    file_import_job = ClientImportFileSeeds.FileImportJob( path )
                    
                    file_import_job.GenerateHashAndStatus()
                    
                    file_import_job.GenerateInfo()
                    
                    self._write( 'import_file', file_import_job )
                    
                
                test_no_sibs()
                
            
            # some sibs that should do nothing
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'process these', 'nope' ) ) )
            
            service_keys_to_content_updates[ self._my_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'mc bad', 'mc wrong' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'pc bad', 'pc wrong' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'pp bad', 'pp wrong' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'sameus aran', 'link' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'link', 'zelda' ) ) )
            
            service_keys_to_content_updates[ self._processing_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), { 'process these' : 'nope' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), { 'mc bad' : 'mc wrong', 'pc bad' : 'pc wrong', 'pp bad' : 'pp wrong', 'sameus aran' : 'zelda', 'link' : 'zelda' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            test_no_sibs()
            
            # remove them
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'process these', 'nope' ) ) )
            
            service_keys_to_content_updates[ self._my_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'mc bad', 'mc wrong' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'pc bad', 'pc wrong' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'pp bad', 'pp wrong' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'sameus aran', 'link' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'link', 'zelda' ) ) )
            
            service_keys_to_content_updates[ self._processing_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            test_no_sibs()
            
            # now some simple sibs
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'mc bad', 'mc good' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'sameus aran', 'samus metroid' ) ) )
            
            service_keys_to_content_updates[ self._my_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'pc bad', 'pc good' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'pp bad', 'pp good' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'samus metroid', 'character:samus aran' ) ) )
            
            service_keys_to_content_updates[ self._public_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), { 'mc bad' : 'mc good', 'sameus aran' : 'samus metroid' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), { 'pc bad' : 'pc good', 'pp bad' : 'pp good', 'samus metroid' : 'character:samus aran' } )
            
            for do_regen_sibs in ( False, True ):
                
                if do_regen_sibs:
                    
                    self._write( 'regenerate_tag_siblings_cache' )
                    
                    self._sync_display()
                    
                
                for do_regen_display in ( False, True ):
                    
                    if do_regen_display:
                        
                        self._write( 'regenerate_tag_display_mappings_cache' )
                        
                        self._sync_display()
                        
                    
                    hash_ids_to_tags_managers = self._read( 'force_refresh_tags_managers', self._hash_ids )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'samus metroid' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'samus metroid', 'process these', 'pc good', 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'mc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good', 'pc good', 'character:samus aran' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good', 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'mc good', 'process these', 'pc good', 'pc good', 'character:samus aran', 'pp good', 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good', 'character:samus aran' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'process these', 'pc good', 'pp good', 'character:samus aran' } )
                    
                    # now we get more write a/c suggestions, and accurated merged read a/c values
                    test_ac( 'mc bad*', self._my_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ), 'mc good' : ( 2, None, 0, None ) }, { 'mc good' : ( 3, None, 0, None ) } )
                    test_ac( 'pc bad*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ), 'pc good' : ( 2, None, 0, None ) }, { 'pc good' : ( 3, None, 0, None ) } )
                    test_ac( 'pp bad*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ), 'pp good' : ( 0, None, 2, None ) }, { 'pp good' : ( 0, None, 3, None ) } )
                    test_ac( 'sameus aran*', self._my_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'samus metroid' : ( 1, None, 0, None ) } )
                    test_ac( 'samus metroid*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                    test_ac( 'samus aran*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                    
                    if on_local_files:
                        
                        # same deal, just smaller file domain
                        test_ac( 'mc bad*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ), 'mc good' : ( 2, None, 0, None ) }, { 'mc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pc bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ), 'pc good' : ( 2, None, 0, None ) }, { 'pc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pp bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ), 'pp good' : ( 0, None, 2, None ) }, { 'pp good' : ( 0, None, 3, None ) } )
                        test_ac( 'sameus aran*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'samus metroid' : ( 1, None, 0, None ) } )
                        test_ac( 'samus metroid*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                        test_ac( 'samus aran*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                        
                        test_ac( 'mc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ), 'mc good' : ( 2, None, 0, None ) }, { 'mc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ), 'pc good' : ( 2, None, 0, None ) }, { 'pc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pp bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ), 'pp good' : ( 0, None, 2, None ) }, { 'pp good' : ( 0, None, 3, None ) } )
                        # here the write a/c gets funky because of all known tags. finding counts for disjoint yet now merged sibling suggestions even though not on same tag domain
                        # slightly odd situation, but we'll want to clear it up
                        # this is cleared up UI side when it does sibling_tag_id filtering based on the tag service we are pending to, but it shows that a/c fetch needs an optional sibling_tag_service_key
                        # this is a job for tag search context
                        # read a/c counts are fine
                        test_ac( 'sameus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ), 'samus metroid' : ( 1, None, 0, None ) }, { 'samus metroid' : ( 1, None, 0, None ) } )
                        test_ac( 'samus metroid*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ), 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 1, None, 1, None ) } )
                        test_ac( 'samus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 1, None, 1, None ) } )
                        
                    else:
                        
                        test_ac( 'mc bad*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pc bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pp bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'sameus aran*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus metroid*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus aran*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        
                        test_ac( 'mc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pp bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'sameus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus metroid*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        
                    
                
            
            # remove the application
            
            master_service_keys_to_parent_applicable_service_keys = { self._my_service_key : [], self._processing_service_key : [], self._public_service_key : [] }
            
            master_service_keys_to_sibling_applicable_service_keys = { self._my_service_key : [], self._processing_service_key : [], self._public_service_key : [] }
            
            self._write( 'tag_display_application', master_service_keys_to_sibling_applicable_service_keys, master_service_keys_to_parent_applicable_service_keys )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            test_no_sibs()
            
            # apply across to both, which should do A->B->C chain
            
            master_service_keys_to_sibling_applicable_service_keys = { self._my_service_key : [ self._my_service_key, self._public_service_key ], self._processing_service_key : [], self._public_service_key : [ self._my_service_key, self._public_service_key ] }
            
            self._write( 'tag_display_application', master_service_keys_to_sibling_applicable_service_keys, master_service_keys_to_parent_applicable_service_keys )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), { 'mc bad' : 'mc good', 'sameus aran' : 'character:samus aran', 'pc bad' : 'pc good', 'pp bad' : 'pp good', 'samus metroid' : 'character:samus aran' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), { 'mc bad' : 'mc good', 'sameus aran' : 'character:samus aran', 'pc bad' : 'pc good', 'pp bad' : 'pp good', 'samus metroid' : 'character:samus aran' } )
            
            for do_regen_sibs in ( False, True ):
                
                if do_regen_sibs:
                    
                    self._write( 'regenerate_tag_siblings_cache' )
                    
                    self._sync_display()
                    
                
                for do_regen_display in ( False, True ):
                    
                    if do_regen_display:
                        
                        self._write( 'regenerate_tag_display_mappings_cache' )
                        
                        self._sync_display()
                        
                    
                    hash_ids_to_tags_managers = self._read( 'force_refresh_tags_managers', self._hash_ids )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'character:samus aran' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_bad_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'character:samus aran', 'process these', 'pc good', 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'mc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good', 'pc good', 'character:samus aran' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good', 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_both_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'mc good', 'process these', 'pc good', 'pc good', 'character:samus aran', 'pp good', 'pp good' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._my_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._processing_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'process these' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrent( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pc good' } )
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetPending( self._public_service_key, ClientTags.TAG_DISPLAY_ACTUAL ), { 'pp good', 'character:samus aran' } )
                    
                    self.assertEqual( hash_ids_to_tags_managers[ self._samus_good_hash_id ].GetCurrentAndPending( CC.COMBINED_TAG_SERVICE_KEY, ClientTags.TAG_DISPLAY_ACTUAL ), { 'mc good', 'process these', 'pc good', 'pp good', 'character:samus aran' } )
                    
                    # now we get more write a/c suggestions, and accurated merged read a/c values
                    test_ac( 'mc bad*', self._my_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ), 'mc good' : ( 2, None, 0, None ) }, { 'mc good' : ( 3, None, 0, None ) } )
                    test_ac( 'pc bad*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ), 'pc good' : ( 2, None, 0, None ) }, { 'pc good' : ( 3, None, 0, None ) } )
                    test_ac( 'pp bad*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ), 'pp good' : ( 0, None, 2, None ) }, { 'pp good' : ( 0, None, 3, None ) } )
                    test_ac( 'sameus aran*', self._my_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'character:samus aran' : ( 1, None, 0, None ) } )
                    test_ac( 'samus metroid*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                    test_ac( 'samus aran*', self._public_service_key, CC.COMBINED_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                    
                    if on_local_files:
                        
                        # same deal, just smaller file domain
                        test_ac( 'mc bad*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ), 'mc good' : ( 2, None, 0, None ) }, { 'mc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pc bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ), 'pc good' : ( 2, None, 0, None ) }, { 'pc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pp bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ), 'pp good' : ( 0, None, 2, None ) }, { 'pp good' : ( 0, None, 3, None ) } )
                        test_ac( 'sameus aran*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ) }, { 'character:samus aran' : ( 1, None, 0, None ) } )
                        test_ac( 'samus metroid*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                        test_ac( 'samus aran*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, { 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, None, 1, None ) } )
                        
                        test_ac( 'mc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'mc bad' : ( 2, None, 0, None ), 'mc good' : ( 2, None, 0, None ) }, { 'mc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'pc bad' : ( 2, None, 0, None ), 'pc good' : ( 2, None, 0, None ) }, { 'pc good' : ( 3, None, 0, None ) } )
                        test_ac( 'pp bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'pp bad' : ( 0, None, 2, None ), 'pp good' : ( 0, None, 2, None ) }, { 'pp good' : ( 0, None, 3, None ) } )
                        # here the write a/c gets funky because of all known tags. finding counts for disjoint yet now merged sibling suggestions even though not on same tag domain
                        # slightly odd situation, but we'll want to clear it up
                        # this is cleared up UI side when it does sibling_tag_id filtering based on the tag service we are pending to, but it shows that a/c fetch needs an optional sibling_tag_service_key
                        # this is a job for tag search context
                        # read a/c counts are fine
                        test_ac( 'sameus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ), 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, 2, 1, None ) } )
                        test_ac( 'samus metroid*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ), 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, 2, 1, None ) } )
                        test_ac( 'samus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, { 'sameus aran' : ( 1, None, 0, None ), 'samus metroid' : ( 1, None, 0, None ), 'character:samus aran' : ( 0, None, 1, None ) }, { 'character:samus aran' : ( 1, 2, 1, None ) } )
                        
                    else:
                        
                        test_ac( 'mc bad*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pc bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pp bad*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'sameus aran*', self._my_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus metroid*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus aran*', self._public_service_key, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        
                        test_ac( 'mc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pc bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'pp bad*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'sameus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus metroid*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        test_ac( 'samus aran*', CC.COMBINED_TAG_SERVICE_KEY, CC.LOCAL_FILE_SERVICE_KEY, {}, {} )
                        
                    
                
            
            # delete and petition, should remove it all
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'mc bad', 'mc good' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_DELETE, ( 'sameus aran', 'samus metroid' ) ) )
            
            service_keys_to_content_updates[ self._my_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PETITION, ( 'pc bad', 'pc good' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PETITION, ( 'pp bad', 'pp good' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PETITION, ( 'samus metroid', 'character:samus aran' ) ) )
            
            service_keys_to_content_updates[ self._public_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            test_no_sibs()
            
            # now test de-looping
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'good answer', 'process these' ) ) )
            
            service_keys_to_content_updates[ self._my_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'process these', 'lmao' ) ) )
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'lmao', 'good answer' ) ) )
            
            service_keys_to_content_updates[ self._processing_service_key ] = content_updates
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_PETITION, ( 'lmao', 'process these' ) ) )
            
            service_keys_to_content_updates[ self._public_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            master_service_keys_to_sibling_applicable_service_keys = { self._my_service_key : [], self._processing_service_key : [ self._processing_service_key, self._my_service_key ], self._public_service_key : [] }
            
            self._write( 'tag_display_application', master_service_keys_to_sibling_applicable_service_keys, master_service_keys_to_parent_applicable_service_keys )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), { 'process these' : 'good answer', 'lmao' : 'good answer' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            master_service_keys_to_sibling_applicable_service_keys = { self._my_service_key : [], self._processing_service_key : [ self._processing_service_key, self._public_service_key ], self._public_service_key : [] }
            
            self._write( 'tag_display_application', master_service_keys_to_sibling_applicable_service_keys, master_service_keys_to_parent_applicable_service_keys )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), { 'process these' : 'good answer', 'lmao' : 'good answer' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            master_service_keys_to_sibling_applicable_service_keys = { self._my_service_key : [], self._processing_service_key : [ self._processing_service_key, self._my_service_key, self._public_service_key ], self._public_service_key : [] }
            
            self._write( 'tag_display_application', master_service_keys_to_sibling_applicable_service_keys, master_service_keys_to_parent_applicable_service_keys )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._processing_service_key ), { 'process these' : 'good answer', 'lmao' : 'good answer' } )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
            content_updates = []
            
            content_updates.append( HydrusData.ContentUpdate( HC.CONTENT_TYPE_TAG_SIBLINGS, HC.CONTENT_UPDATE_ADD, ( 'good answer', 'process these' ) ) )
            
            service_keys_to_content_updates[ self._processing_service_key ] = content_updates
            
            service_keys_to_content_updates[ self._public_service_key ] = content_updates
            
            self._write( 'content_updates', service_keys_to_content_updates )
            
            self._sync_display()
            
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._my_service_key ), {} )
            self.assertEqual( len( self._read( 'tag_siblings_all_ideals', self._processing_service_key ) ), 2 )
            self.assertEqual( self._read( 'tag_siblings_all_ideals', self._public_service_key ), {} )
            
        


    '''
class TestTagParents( unittest.TestCase ):
    
    @classmethod
    def setUpClass( cls ):
        
        cls._first_key = HydrusData.GenerateKey()
        cls._second_key = HydrusData.GenerateKey()
        cls._third_key = HydrusData.GenerateKey()
        
        first_dict = HydrusData.default_dict_set()
        
        first_dict[ HC.CONTENT_STATUS_CURRENT ] = { ( 'current_a', 'current_b' ), ( 'child', 'mother' ), ( 'child', 'father' ), ( 'sister', 'mother' ), ( 'sister', 'father' ), ( 'brother', 'mother' ), ( 'brother', 'father' ), ( 'mother', 'grandmother' ), ( 'mother', 'grandfather' ), ( 'aunt', 'grandmother' ), ( 'aunt', 'grandfather' ), ( 'cousin', 'aunt' ), ( 'cousin', 'uncle' ), ( 'closed_loop', 'closed_loop' ), ( 'loop_a', 'loop_b' ), ( 'loop_b', 'loop_c' ) }
        first_dict[ HC.CONTENT_STATUS_DELETED ] = { ( 'deleted_a', 'deleted_b' ) }
        
        second_dict = HydrusData.default_dict_set()
        
        second_dict[ HC.CONTENT_STATUS_CURRENT ] = { ( 'loop_c', 'loop_a' ) }
        second_dict[ HC.CONTENT_STATUS_DELETED ] = { ( 'current_a', 'current_b' ) }
        second_dict[ HC.CONTENT_STATUS_PENDING ] = { ( 'pending_a', 'pending_b' ) }
        second_dict[ HC.CONTENT_STATUS_PETITIONED ] = { ( 'petitioned_a', 'petitioned_b' ) }
        
        third_dict = HydrusData.default_dict_set()
        
        third_dict[ HC.CONTENT_STATUS_CURRENT ] = { ( 'petitioned_a', 'petitioned_b' ) }
        third_dict[ HC.CONTENT_STATUS_DELETED ] = { ( 'pending_a', 'pending_b' ) }
        
        tag_parents = collections.defaultdict( HydrusData.default_dict_set )
        
        tag_parents[ cls._first_key ] = first_dict
        tag_parents[ cls._second_key ] = second_dict
        tag_parents[ cls._third_key ] = third_dict
        
        HG.test_controller.SetRead( 'tag_parents', tag_parents )
        
        cls._tag_parents_manager = ClientManagers.TagParentsManager( HG.client_controller )
        
    
    def test_expand_predicates( self ):
        
        predicates = []
        
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'grandmother', min_current_count = 10 ) )
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'grandfather', min_current_count = 15 ) )
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'not_exist', min_current_count = 20 ) )
        
        self.assertEqual( self._tag_parents_manager.ExpandPredicates( CC.COMBINED_TAG_SERVICE_KEY, predicates ), predicates )
        
        predicates = []
        
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'child', min_current_count = 10 ) )
        
        results = []
        
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'child', min_current_count = 10 ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'mother' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'father' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'grandmother' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'grandfather' ) )
        
        self.assertEqual( set( self._tag_parents_manager.ExpandPredicates( CC.COMBINED_TAG_SERVICE_KEY, predicates ) ), set( results ) )
        
        predicates = []
        
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_NAMESPACE, 'series' ) )
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'child', min_current_count = 10 ) )
        predicates.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'cousin', min_current_count = 5 ) )
        
        results = []
        
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_NAMESPACE, 'series' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'child', min_current_count = 10 ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'mother' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'father' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'grandmother' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'grandfather' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_TAG, 'cousin', min_current_count = 5 ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'aunt' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'uncle' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'grandmother' ) )
        results.append( ClientSearch.Predicate( ClientSearch.PREDICATE_TYPE_PARENT, 'grandfather' ) )
        
        self.assertEqual( set( self._tag_parents_manager.ExpandPredicates( CC.COMBINED_TAG_SERVICE_KEY, predicates ) ), set( results ) )
        
    
    def test_expand_tags( self ):
        
        tags = { 'grandmother', 'grandfather' }
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, tags ), tags )
        
        tags = { 'child', 'cousin' }
        
        results = { 'child', 'mother', 'father', 'grandmother', 'grandfather', 'cousin', 'aunt', 'uncle', 'grandmother', 'grandfather' }
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, tags ), results )
        
    
    def test_grandparents( self ):
        
        self.assertEqual( set( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'child' ) ), { 'mother', 'father', 'grandmother', 'grandfather' } )
        self.assertEqual( set( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'mother' ) ), { 'grandmother', 'grandfather' } )
        self.assertEqual( set( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'grandmother' ) ), set() )
        
    
    def test_current_overwrite( self ):
        
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'current_a' ), [ 'current_b' ] )
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'current_b' ), [] )
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'current_a' ] ), { 'current_a', 'current_b' } )
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'current_b' ] ), { 'current_b' } )
        
    
    def test_deleted( self ):
        
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'deleted_a' ), [] )
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'deleted_b' ), [] )
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'deleted_a' ] ), { 'deleted_a' } )
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'deleted_b' ] ), { 'deleted_b' } )
        
    
    def test_no_loop( self ):
        
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'closed_loop' ), [] )
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'closed_loop' ] ), { 'closed_loop' } )
        
    
    def test_not_exist( self ):
        
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'not_exist' ), [] )
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'not_exist' ] ), { 'not_exist' } )
        
    
    def test_pending_overwrite( self ):
        
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'pending_a' ), [ 'pending_b' ] )
        self.assertEqual( self._tag_parents_manager.GetParents( CC.COMBINED_TAG_SERVICE_KEY, 'pending_b' ), [] )
        
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'pending_a' ] ), { 'pending_a', 'pending_b' } )
        self.assertEqual( self._tag_parents_manager.ExpandTags( CC.COMBINED_TAG_SERVICE_KEY, [ 'pending_b' ] ), { 'pending_b' } )
        
    '''
