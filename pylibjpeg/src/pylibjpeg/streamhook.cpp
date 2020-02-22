// Includes
#include <iostream>
#include "streamhook.hpp"
#include "decode.hpp"
#include "../libjpeg/interface/hooks.hpp"
#include "../libjpeg/interface/tagitem.hpp"
#include "../libjpeg/interface/parameters.hpp"
#include "std/stdio.hpp"

// The IO hook function
JPG_LONG StreamHook(struct JPG_Hook *hook, struct JPG_TagItem *tags)
{
    // Pointer to the input data which is stored by the hook
    // Need to customise the hook so we can add the length of the input data
    StreamData *in = (StreamData *)(hook->hk_pData);
    char *data = (char *)(in->pData);

    std::cout << "Current position: " << in->position << std::endl;
    std::cout << "Moving pointer to position" << std::endl;
    printf("Initial position 0x%X, value 0x%X\n", data, *data);
    // init, condition, increase
    // repeats while condition is true
    int total_move = 0;
    for (int ii = 0; ii < in->position; ii++) {
        total_move += 1;
        data++;
    }
    std::cout << "Moved " << total_move << std::endl;
    printf("Final position 0x%X, value 0x%X\n", data, *data);

    switch(tags->GetTagData(JPGTAG_FIO_ACTION)) {
        case JPGFLAG_ACTION_READ:
        {
            UBYTE *buffer = (UBYTE *)tags->GetTagPtr(JPGTAG_FIO_BUFFER);
            ULONG  size   = (ULONG  )tags->GetTagData(JPGTAG_FIO_SIZE);

            std::cout << "Reading " << size << " bytes starting at " << in->position << std::endl;

            // Number of bytes read this session
            ULONG bytes_read = 0;
            // TODO dont allow reading beyond end
            for (int ii = 0; ii < size; ii++) {
                if (in->nr_read >= in->length) {
                    break;
                }
                //std::cout << *in << std::endl;
                // Copy value at current input item to buffer
                *buffer = *data;
                in->nr_read += 1;
                in->position += 1;
                bytes_read += 1;
                // Increment buffer pointer
                buffer++;
                // Increment input pointer
                data++;
            }

            std::cout << "Read " << bytes_read << " now at " << in->position << std::endl;

            //int nr_read = fread(buffer, 1, size, in);
            //std::cout << "read " << bytes_read << " total " << in->nr_read << std::endl;
            return bytes_read;
        }
        case JPGFLAG_ACTION_WRITE:
        {
            UBYTE *buffer = (UBYTE *)tags->GetTagPtr(JPGTAG_FIO_BUFFER);
            ULONG  size   = (ULONG  )tags->GetTagData(JPGTAG_FIO_SIZE);

            std::cout << "Need to write" << std::endl;

            /*
            std::cout << "writing... \n";
            int nr_write = fwrite(buffer, 1, size, in);
            std::cout << "write " << nr_write << std::endl;
            return nr_write;
            */
            return 0;
        }
        case JPGFLAG_ACTION_SEEK:
        {
            LONG mode   = tags->GetTagData(JPGTAG_FIO_SEEKMODE);
            LONG offset = tags->GetTagData(JPGTAG_FIO_OFFSET);

            std::cout << "Current position " << in->position << std::endl;
            std::cout << "Move " << offset;

            int result = 0;
            switch(mode) {
                case JPGFLAG_OFFSET_CURRENT:
                    std::cout << " from current" << std::endl;
                    for (int ii = 0; ii <= offset; ii++)
                    {
                        data++;
                        in->position += 1;
                    }
                    return result;
                case JPGFLAG_OFFSET_BEGINNING:
                    std::cout << " from start" << std::endl;
                    //for (int ii = 0; ii < offset, ii++) {
                    //    //
                    //}
                    return result;
                case JPGFLAG_OFFSET_END:
                    std::cout << " from end" << std::endl;
                    return result;
            }
            return 0;
        }
        case JPGFLAG_ACTION_QUERY:
        {
            return 0;
        }
    }
    return -1;
}
