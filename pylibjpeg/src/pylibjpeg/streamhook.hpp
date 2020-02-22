#ifndef PYLIBJPEG_STREAMHOOK_HPP
#define PYLIBJPEG_STREAMHOOK_HPP

// Includes
#include "../libjpeg/interface/types.hpp"


// Forwards
struct JPG_Hook;
struct JPG_TagItem;


// Prototypes
extern JPG_LONG StreamHook(struct JPG_Hook *hook, struct JPG_TagItem *tags);

#endif
