project('hello-world', 'c')

cc = meson.get_compiler('c')

gtk_dep = dependency('gtk-4', version : '>=4.0', required : true)
libadwaita_dep = dependency('libadwaita-1', version : '>=1.0', required : true)

executable('hello-world',
  'src/main.c',
  dependencies : [gtk_dep, libadwaita_dep],
  install : true
)
