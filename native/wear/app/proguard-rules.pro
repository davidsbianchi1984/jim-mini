# Empty on purpose, and referenced on purpose.
#
# `isMinifyEnabled = false` means R8 never reads this file, so an absent
# one costs nothing today. It is named in build.gradle.kts so that the day
# somebody switches minification on, the place to put a keep rule already
# exists and is already in version control — rather than being invented
# under time pressure by whoever is trying to ship a release build.
#
# The phone shell's module makes the same declaration for the same reason.
